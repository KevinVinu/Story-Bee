from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import bcrypt
import os
import requests
import webbrowser
import traceback
from jwt import decode, PyJWTError

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'stories.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'a-very-secure-random-key-12345'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# DeepSeek API Configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    stories = db.relationship('Story', backref='author', lazy=True)
    likes = db.relationship('Likes', backref='user', lazy=True)
    saved_stories = db.relationship('SavedStories', backref='user', lazy=True)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    genre = db.Column(db.String(50), nullable=True)
    likes = db.relationship('Likes', backref='story', lazy=True)
    saved_by = db.relationship('SavedStories', backref='story', lazy=True)

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'story_id', name='unique_like'),)

class SavedStories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'story_id', name='unique_save'),)

with app.app_context():
    db.create_all()

    if not User.query.first():
        user1 = User(username='kevin', password_hash=bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()))
        user2 = User(username='alex', password_hash=bcrypt.hashpw('password456'.encode('utf-8'), bcrypt.gensalt()))
        db.session.add_all([user1, user2])
        db.session.commit()

        dummy_stories = [
            Story(title='The High Bee', content='Once upon a time, a bee got lost...', user_id=user1.id, 
                  image_url='https://cdn.pixabay.com/photo/2017/10/21/20/14/bee-2874979_1280.jpg', genre='Adventure'),
            Story(title='Whispers in the Wind', content='The breeze carried secrets...', user_id=user2.id, 
                  image_url='https://images.unsplash.com/photo-1506744038136-46273834b3fb', genre='Mystery'),
            Story(title='Laughing Shadows', content='A shadow told a joke...', user_id=user1.id, 
                  image_url='https://images.unsplash.com/photo-1516534775068-ba3e7458af70', genre='Comedy'),
            Story(title='The Haunted Hive', content='A hive turned spooky...', user_id=user2.id, 
                  image_url='https://images.unsplash.com/photo-1503435980610-a51f3ddfee50', genre='Horror'),
        ]
        db.session.add_all(dummy_stories)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=username, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token, "username": user.username}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/submit_story', methods=['POST'])
@jwt_required()
def submit_story():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        title = data.get('title')
        content = data.get('content')
        image_url = data.get('image_url', 'https://picsum.photos/200/300?random=5')
        genre = data.get('genre', None)
        user_id = get_jwt_identity()

        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400
        
        new_story = Story(title=title, content=content, user_id=user_id, image_url=image_url, genre=genre)
        db.session.add(new_story)
        db.session.commit()
        return jsonify({"message": "Story submitted", "id": new_story.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in submit_story: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/get_stories', methods=['GET'])
def get_stories():
    user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        try:
            decoded = decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            user_id = decoded.get('sub')  # 'sub' is the default identity claim
        except PyJWTError:
            pass  # Invalid token, treat as unauthenticated

    genre = request.args.get('genre')
    query = Story.query
    if genre:
        query = query.filter_by(genre=genre)
    stories = query.all()
    story_list = []
    for s in stories:
        like_count = Likes.query.filter_by(story_id=s.id).count()
        is_liked = user_id and Likes.query.filter_by(user_id=user_id, story_id=s.id).first() is not None
        is_saved = user_id and SavedStories.query.filter_by(user_id=user_id, story_id=s.id).first() is not None
        story_list.append({
            "id": s.id, "title": s.title, "content": s.content, "created_at": s.created_at.isoformat(), 
            "author": s.author.username, "image_url": s.image_url, "genre": s.genre,
            "like_count": like_count, "is_liked": is_liked, "is_saved": is_saved
        })
    return jsonify(story_list), 200

@app.route('/like_story', methods=['POST'])
@jwt_required()
def like_story():
    user_id = get_jwt_identity()
    data = request.get_json()
    story_id = data.get('story_id')
    if not story_id or not Story.query.get(story_id):
        return jsonify({"error": "Invalid story ID"}), 400
    
    like = Likes.query.filter_by(user_id=user_id, story_id=story_id).first()
    if like:
        db.session.delete(like)  # Unlike
        db.session.commit()
        return jsonify({"message": "Story unliked"}), 200
    else:
        new_like = Likes(user_id=user_id, story_id=story_id)
        db.session.add(new_like)  # Like
        db.session.commit()
        return jsonify({"message": "Story liked"}), 200

@app.route('/save_story', methods=['POST'])
@jwt_required()
def save_story():
    user_id = get_jwt_identity()
    data = request.get_json()
    story_id = data.get('story_id')
    if not story_id or not Story.query.get(story_id):
        return jsonify({"error": "Invalid story ID"}), 400
    
    saved = SavedStories.query.filter_by(user_id=user_id, story_id=story_id).first()
    if saved:
        db.session.delete(saved)  # Unsave
        db.session.commit()
        return jsonify({"message": "Story unsaved"}), 200
    else:
        new_save = SavedStories(user_id=user_id, story_id=story_id)
        db.session.add(new_save)  # Save
        db.session.commit()
        return jsonify({"message": "Story saved"}), 200

@app.route('/generate_story', methods=['POST'])
@jwt_required()
def generate_story():
    data = request.get_json()
    partial_story = data.get('partial_story')
    title = data.get('title', 'AI-Generated Story')
    image_url = data.get('image_url', 'https://picsum.photos/200/300?random=6')
    genre = data.get('genre', None)
    if not partial_story:
        return jsonify({"error": "Partial story is required"}), 400

    # DeepSeek API call
    system_prompt = (
        "You are StoryBee AI, a creative and professional storyteller. "
        "The user gives the beginning of a story, and you continue and complete it as a short story "
        "with a clear and satisfying ending. "
        "Respond only with the completed story—no chatbot replies, no explanations, no greetings."
    )

    payload = {
        "model": "deepseek/deepseek-r1:free1",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": partial_story}
        ],
        "temperature": 0.9
    }

    try:
        print(f"Sending request to DeepSeek API with payload: {payload}")
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        print(f"API response status: {response.status_code}")
        print(f"API response body: {response.text}")
        if response.status_code == 200:
            continuation = response.json()["choices"][0]["message"]["content"].strip()
            return jsonify({"continuation": continuation}), 200
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            print(error_msg)
            return jsonify({"error": error_msg}), 500
    except Exception as e:
        error_msg = f"Error calling DeepSeek API: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({"error": "Failed to generate story", "details": str(e)}), 500

if __name__ == '__main__':
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        webbrowser.open('http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)