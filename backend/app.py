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
# Enable CORS for the frontend domain
CORS(app, resources={r"/*": {
    "origins": ["https://bestill-frontend.onrender.com", "http://localhost:5000"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

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

# Sample data - Daily Miracle Facts
facts = [
    {
        "fact": "In this exact moment, your body is creating 300 billion new cells - that's like building an entire city of microscopic life every single minute.",
        "details": "YOU'VE JUST CREATED MORE CELLS THAN THERE ARE STARS IN 1,000 GALAXIES COMBINED. EACH OF THESE CELLS IS A MASTERPIECE, CONTAINING DNA SO COMPLEX IT WOULD TAKE 1,000 BOOKS TO WRITE DOWN THE CODE FOR JUST ONE CELL. THIS EXTRAORDINARY PROCESS CONTINUES EVERY SINGLE MINUTE, WHETHER YOU'RE AWAKE OR DEEP IN SLEEP. YOUR BODY IS RUNNING THE MOST SOPHISTICATED FACTORY IN THE UNIVERSE, AND IT NEVER STOPS. THIS LEVEL OF PRECISION AND COMPLEXITY COULD ONLY COME FROM A DIVINE BLUEPRINT - YOU ARE A LIVING TESTAMENT TO GOD'S INCREDIBLE DESIGN.",
        "verse": "Psalm 139:14 - I praise you because I am fearfully and wonderfully made; your works are wonderful, I know that full well.",
        "cellsPerMinute": 300000000000
    },
    {
        "fact": "Your brain processes information at an astounding speed of 268 mph - faster than the world's fastest race car!",
        "details": "IN A SINGLE SECOND, YOUR BRAIN COMPLETES OVER 100,000 CHEMICAL REACTIONS. THIS INCREDIBLE NEURAL NETWORK CONTAINS 86 BILLION NEURONS, EACH ONE CONNECTED TO 10,000 OTHERS, CREATING A VAST UNIVERSE OF THOUGHTS AND MEMORIES. EVERY TIME YOU RECALL A MEMORY OR LEARN SOMETHING NEW, YOUR BRAIN PHYSICALLY REWIRES ITSELF. THIS DIVINE ENGINEERING SURPASSES ANY SUPERCOMPUTER EVER BUILT - A TESTAMENT TO GOD'S EXTRAORDINARY CRAFTSMANSHIP IN CREATING YOU.",
        "verse": "Isaiah 55:9 - As the heavens are higher than the earth, so are my ways higher than your ways and my thoughts than your thoughts.",
        "cellsPerMinute": 300000000000
    },
    {
        "fact": "Your heart will beat approximately 115,000 times today, pumping life-giving blood through 60,000 miles of blood vessels.",
        "details": "THE INCREDIBLE JOURNEY OF YOUR BLOOD VESSELS, IF LAID END TO END, WOULD CIRCLE THE EARTH TWICE! EVERY SECOND, 2 MILLION NEW BLOOD CELLS ARE BORN IN YOUR BONE MARROW, EACH ONE PRECISELY CRAFTED FOR ITS LIFE-GIVING MISSION. YOUR HEART, NO LARGER THAN YOUR FIST, WILL PUMP ABOUT 2,000 GALLONS OF BLOOD TODAY - ENOUGH TO FILL A SMALL SWIMMING POOL. THIS MIRACULOUS SYSTEM WORKS TIRELESSLY, DAY AND NIGHT, FROM YOUR FIRST MOMENT TO YOUR LAST - A PERFECT EXAMPLE OF GOD'S INTRICATE AND LOVING DESIGN.",
        "verse": "Jeremiah 1:5 - Before I formed you in the womb I knew you, before you were born I set you apart.",
        "cellsPerMinute": 300000000000
    }
]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Prayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    replies = db.relationship('PrayerReply', backref='prayer', lazy=True)

class PrayerReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prayer_id = db.Column(db.Integer, db.ForeignKey('prayer.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)

class Praise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    replies = db.relationship('DiscussionReply', backref='discussion', lazy=True)

class DiscussionReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)

@app.route('/api/fact', methods=['GET'])
def get_fact():
    try:
        # Get today's date and use it to select a fact
        today = datetime.now().date()
        # Use the day of the year to rotate through facts
        fact_index = (today.timetuple().tm_yday - 1) % len(facts)
        logger.debug(f'Serving fact index {fact_index} for date {today}')
        return jsonify(facts[fact_index])
    except Exception as e:
        logger.error(f"Error in get_fact: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/prayers', methods=['GET'])
def get_prayers():
    prayers = Prayer.query.order_by(Prayer.timestamp.desc()).all()
    prayers_list = []
    for prayer in prayers:
        replies = [{'id': r.id, 'name': r.name, 'content': r.content, 
                   'timestamp': r.timestamp.isoformat(), 'likes': r.likes} 
                  for r in prayer.replies]
        prayers_list.append({
            'id': prayer.id,
            'name': prayer.name,
            'content': prayer.content,
            'timestamp': prayer.timestamp.isoformat(),
            'likes': prayer.likes,
            'replies': replies
        })
    return jsonify(prayers_list)

@app.route('/api/prayers/<int:prayer_id>/reply', methods=['POST'])
def add_prayer_reply(prayer_id):
    data = request.get_json()
    reply = PrayerReply(
        prayer_id=prayer_id,
        name=data['name'],
        content=data['content']
    )
    db.session.add(reply)
    db.session.commit()
    return jsonify({
        'id': reply.id,
        'name': reply.name,
        'content': reply.content,
        'timestamp': reply.timestamp.isoformat(),
        'likes': reply.likes
    })

@app.route('/api/prayers/<int:prayer_id>/like', methods=['POST'])
def like_prayer(prayer_id):
    prayer = Prayer.query.get_or_404(prayer_id)
    prayer.likes += 1
    db.session.commit()
    return jsonify({'likes': prayer.likes})

@app.route('/api/prayers/replies/<int:reply_id>/like', methods=['POST'])
def like_prayer_reply(reply_id):
    reply = PrayerReply.query.get_or_404(reply_id)
    reply.likes += 1
    db.session.commit()
    return jsonify({'likes': reply.likes})

@app.route('/api/discussions', methods=['GET'])
def get_discussions():
    discussions = Discussion.query.order_by(Discussion.timestamp.desc()).all()
    discussions_list = []
    for discussion in discussions:
        replies = [{'id': r.id, 'name': r.name, 'content': r.content, 
                   'timestamp': r.timestamp.isoformat(), 'likes': r.likes} 
                  for r in discussion.replies]
        discussions_list.append({
            'id': discussion.id,
            'name': discussion.name,
            'content': discussion.content,
            'timestamp': discussion.timestamp.isoformat(),
            'likes': discussion.likes,
            'replies': replies
        })
    return jsonify(discussions_list)

@app.route('/api/discussions/<int:discussion_id>/reply', methods=['POST'])
def add_discussion_reply(discussion_id):
    data = request.get_json()
    reply = DiscussionReply(
        discussion_id=discussion_id,
        name=data['name'],
        content=data['content']
    )
    db.session.add(reply)
    db.session.commit()
    return jsonify({
        'id': reply.id,
        'name': reply.name,
        'content': reply.content,
        'timestamp': reply.timestamp.isoformat(),
        'likes': reply.likes
    })

@app.route('/api/discussions/<int:discussion_id>/like', methods=['POST'])
def like_discussion(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)
    discussion.likes += 1
    db.session.commit()
    return jsonify({'likes': discussion.likes})

@app.route('/api/discussions/replies/<int:reply_id>/like', methods=['POST'])
def like_discussion_reply(reply_id):
    reply = DiscussionReply.query.get_or_404(reply_id)
    reply.likes += 1
    db.session.commit()
    return jsonify({'likes': reply.likes})

@app.route('/api/praises', methods=['GET', 'POST'])
def handle_praises():
    if request.method == 'GET':
        praises = Praise.query.order_by(Praise.timestamp.desc()).all()
        return jsonify([{
            'id': praise.id,
            'content': praise.content,
            'author': praise.author,
            'timestamp': praise.timestamp.isoformat()
        } for praise in praises])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_praise = Praise(
            content=data['content'],
            author=data['author'],
            timestamp=datetime.utcnow()
        )
        db.session.add(new_praise)
        db.session.commit()
        return jsonify({
            'id': new_praise.id,
            'content': new_praise.content,
            'author': new_praise.author,
            'timestamp': new_praise.timestamp.isoformat()
        }), 201

@app.route('/api/discussions', methods=['GET', 'POST'])
def handle_discussions():
    if request.method == 'GET':
        discussions = Discussion.query.order_by(Discussion.timestamp.desc()).all()
        return jsonify([{
            'id': discussion.id,
            'name': discussion.name,
            'content': discussion.content,
            'timestamp': discussion.timestamp.isoformat(),
            'likes': discussion.likes,
            'replies': [{'id': r.id, 'name': r.name, 'content': r.content, 
                        'timestamp': r.timestamp.isoformat(), 'likes': r.likes} 
                       for r in discussion.replies]
        } for discussion in discussions])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_discussion = Discussion(
            name=data['name'],
            content=data['content'],
            timestamp=datetime.utcnow()
        )
        db.session.add(new_discussion)
        db.session.commit()
        return jsonify({
            'id': new_discussion.id,
            'name': new_discussion.name,
            'content': new_discussion.content,
            'timestamp': new_discussion.timestamp.isoformat(),
            'likes': new_discussion.likes
        }), 201

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)
