from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import firebase_admin
from firebase_admin import credentials, firestore
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# Initialize Firebase
cred = credentials.Certificate("service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return User(user_id, user_data['email'], user_data['password_hash'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Query user by email
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).get()
        
        if not query:
            flash('Invalid email or password')
            return redirect(url_for('login'))
        
        user_doc = query[0]
        user_data = user_doc.to_dict()
        
        if check_password_hash(user_data['password_hash'], password):
            user = User(user_doc.id, user_data['email'], user_data['password_hash'])
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).get()
        
        if query:
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Create new user
        password_hash = generate_password_hash(password)
        user_data = {
            'email': email,
            'password_hash': password_hash
        }
        
        db.collection('users').add(user_data)
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/save_answer', methods=['POST'])
@login_required
def save_answer():
    data = request.get_json()
    answer_key = data.get('key')
    answer_text = data.get('text')
    
    if not answer_key or not answer_text:
        return jsonify({'error': 'Missing key or text'}), 400
    
    # Save answer to Firebase
    user_answers_ref = db.collection('users').document(current_user.id).collection('answers')
    user_answers_ref.document(answer_key).set({
        'text': answer_text,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({'success': True})

@app.route('/get_answers')
@login_required
def get_answers():
    user_answers_ref = db.collection('users').document(current_user.id).collection('answers')
    answers = {}
    
    for doc in user_answers_ref.stream():
        answers[doc.id] = doc.to_dict()['text']
    
    return jsonify(answers)

if __name__ == '__main__':
    app.run(debug=True) 