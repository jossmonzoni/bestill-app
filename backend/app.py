from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend')
# Enable CORS for all domains and methods
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///be_still.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Sample data
facts = [{"fact": "The human body regenerates approximately 300 million cells each day.", "details": "Cells in the human body have different lifespans. Red blood cells last about 120 days, while skin cells regenerate every 2-3 weeks.", "verse": "Psalm 139:14 - I praise you because I am fearfully and wonderfully made; your works are wonderful, I know that full well."}]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(10), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'post_type': self.post_type,
            'author': self.author,
            'created_at': self.created_at.isoformat()
        }

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id'),)

class PostReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'content': self.content,
            'author': self.author,
            'created_at': self.created_at.isoformat()
        }

@app.route('/api/fact', methods=['GET'])
def get_fact():
    return jsonify(facts[0])

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        post_type = request.args.get('type', 'all')
        logger.debug(f'Getting posts of type: {post_type}')
        
        # Base query
        query = Post.query

        # Apply type filter if specified
        if post_type != 'all':
            query = query.filter_by(post_type=post_type)

        # Order by most recent first
        query = query.order_by(Post.created_at.desc())

        # Execute query
        posts = query.all()
        posts_data = [post.to_dict() for post in posts]
        
        logger.debug(f'Found {len(posts_data)} posts')
        return jsonify(posts_data)

    except Exception as e:
        logger.error(f"Error in get_posts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts', methods=['POST'])
def create_post():
    try:
        logger.debug("Received POST request to /api/posts")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        # Handle preflight request
        if request.method == 'OPTIONS':
            return '', 200
            
        data = request.get_json(force=True)  # force=True to handle any content-type
        logger.debug(f"Received data: {data}")
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400

        content = data.get('content')
        post_type = data.get('post_type')
        author = data.get('author', 'Anonymous')
        
        if not content:
            logger.error("Content is required")
            return jsonify({'error': 'Content is required'}), 400
        
        if not post_type:
            logger.error("post_type is required")
            return jsonify({'error': 'post_type is required'}), 400
        
        if post_type not in ['prayer', 'praise']:
            logger.error(f"Invalid post_type: {post_type}")
            return jsonify({'error': 'post_type must be either "prayer" or "praise"'}), 400
        
        logger.debug(f"Creating new post with type: {post_type}")
        new_post = Post(content=content, post_type=post_type, author=author)
        db.session.add(new_post)
        db.session.commit()
        
        response_data = {
            'id': new_post.id,
            'content': content,
            'post_type': post_type,
            'author': author,
            'created_at': new_post.created_at.isoformat(),
            'likes_count': 0,
            'replies_count': 0
        }
        logger.debug(f"Sending response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.exception("Error creating post")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/count', methods=['GET'])
def get_post_count():
    post_type = request.args.get('type', 'all')
    
    try:
        if post_type == 'all':
            count = Post.query.count()
        else:
            count = Post.query.filter_by(post_type=post_type).count()
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Check if post exists
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404

        # Check if user already liked the post
        existing_like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing_like:
            # Unlike the post
            db.session.delete(existing_like)
        else:
            # Like the post
            new_like = PostLike(post_id=post_id, user_id=user_id)
            db.session.add(new_like)

        db.session.commit()

        # Get updated like count
        likes_count = PostLike.query.filter_by(post_id=post_id).count()
        
        return jsonify({
            "message": "Like updated successfully",
            "likes_count": likes_count
        })

    except Exception as e:
        logger.error(f"Error in like_post: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts/<int:post_id>/like/count', methods=['GET'])
def get_like_count(post_id):
    try:
        count = PostLike.query.filter_by(post_id=post_id).count()
        return jsonify({"count": count})
    except Exception as e:
        logger.error(f"Error getting like count: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts/<int:post_id>/replies', methods=['GET'])
def get_replies(post_id):
    try:
        replies = PostReply.query.filter_by(post_id=post_id).all()
        replies_data = [reply.to_dict() for reply in replies]
        return jsonify(replies_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts/<int:post_id>/replies', methods=['POST'])
def create_reply(post_id):
    try:
        data = request.json
        logger.debug(f'Creating reply with data: {data}')
        
        # Validate content
        if not data.get('content'):
            return jsonify({"error": "Content is required"}), 400

        # Create new reply
        new_reply = PostReply(
            post_id=post_id,
            content=data['content'],
            author=data.get('author')
        )

        # Save to database
        db.session.add(new_reply)
        db.session.commit()
        logger.debug(f'Created reply with id: {new_reply.id}')

        return jsonify(new_reply.to_dict()), 201

    except Exception as e:
        logger.error(f"Error in create_reply: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
