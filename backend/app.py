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
    name = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)

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

@app.route('/api/prayers', methods=['GET'])
def get_prayers():
    prayers = Prayer.query.order_by(Prayer.timestamp.desc()).all()
    return jsonify([{
        'id': prayer.id,
        'name': prayer.name,
        'content': prayer.content,
        'timestamp': prayer.timestamp.isoformat(),
        'likes': prayer.likes,
        'replies': [{
            'id': reply.id,
            'name': reply.name,
            'content': reply.content,
            'timestamp': reply.timestamp.isoformat(),
            'likes': reply.likes
        } for reply in prayer.replies]
    } for prayer in prayers])

@app.route('/api/prayers/<int:prayer_id>/reply', methods=['POST'])
def add_prayer_reply(prayer_id):
    try:
        data = request.get_json()
        name = data.get('name')
        content = data.get('content')
        
        if not name or not content:
            return jsonify({'error': 'Name and content are required'}), 400
            
        prayer = Prayer.query.get(prayer_id)
        if not prayer:
            return jsonify({'error': 'Prayer not found'}), 404
            
        reply = PrayerReply(
            prayer_id=prayer_id,
            name=name,
            content=content,
            timestamp=datetime.utcnow(),
            likes=0
        )
        
        db.session.add(reply)
        db.session.commit()
        
        return jsonify({
            'id': reply.id,
            'name': reply.name,
            'content': reply.content,
            'timestamp': reply.timestamp.isoformat(),
            'likes': reply.likes
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prayers/<int:prayer_id>/like', methods=['POST'])
def like_prayer(prayer_id):
    try:
        prayer = Prayer.query.get(prayer_id)
        if not prayer:
            return jsonify({'error': 'Prayer not found'}), 404
            
        prayer.likes += 1
        db.session.commit()
        
        return jsonify({'likes': prayer.likes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prayers/replies/<int:reply_id>/like', methods=['POST'])
def like_prayer_reply(reply_id):
    try:
        reply = PrayerReply.query.get(reply_id)
        if not reply:
            return jsonify({'error': 'Reply not found'}), 404
            
        reply.likes += 1
        db.session.commit()
        
        return jsonify({'likes': reply.likes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/discussions', methods=['GET'])
def get_discussions():
    discussions = Discussion.query.order_by(Discussion.timestamp.desc()).all()
    return jsonify([{
        'id': discussion.id,
        'name': discussion.name,
        'content': discussion.content,
        'timestamp': discussion.timestamp.isoformat(),
        'likes': discussion.likes,
        'replies': [{
            'id': reply.id,
            'name': reply.name,
            'content': reply.content,
            'timestamp': reply.timestamp.isoformat(),
            'likes': reply.likes
        } for reply in discussion.replies]
    } for discussion in discussions])

@app.route('/api/discussions/<int:discussion_id>/reply', methods=['POST'])
def add_discussion_reply(discussion_id):
    try:
        data = request.get_json()
        name = data.get('name')
        content = data.get('content')
        
        if not name or not content:
            return jsonify({'error': 'Name and content are required'}), 400
            
        discussion = Discussion.query.get(discussion_id)
        if not discussion:
            return jsonify({'error': 'Discussion not found'}), 404
            
        reply = DiscussionReply(
            discussion_id=discussion_id,
            name=name,
            content=content,
            timestamp=datetime.utcnow(),
            likes=0
        )
        
        db.session.add(reply)
        db.session.commit()
        
        return jsonify({
            'id': reply.id,
            'name': reply.name,
            'content': reply.content,
            'timestamp': reply.timestamp.isoformat(),
            'likes': reply.likes
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/discussions/<int:discussion_id>/like', methods=['POST'])
def like_discussion(discussion_id):
    try:
        discussion = Discussion.query.get(discussion_id)
        if not discussion:
            return jsonify({'error': 'Discussion not found'}), 404
            
        discussion.likes += 1
        db.session.commit()
        
        return jsonify({'likes': discussion.likes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/discussions/replies/<int:reply_id>/like', methods=['POST'])
def like_discussion_reply(reply_id):
    try:
        reply = DiscussionReply.query.get(reply_id)
        if not reply:
            return jsonify({'error': 'Reply not found'}), 404
            
        reply.likes += 1
        db.session.commit()
        
        return jsonify({'likes': reply.likes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
