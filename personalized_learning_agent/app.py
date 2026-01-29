"""
Personalized Learning Path Agent - Main Flask Application
AI-Driven Web Application for B.Tech CSE Students
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta
import json
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Database configuration
DATABASE = 'learning_agent.db'

def get_db():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables and sample data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Student profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            current_semester INTEGER NOT NULL,
            overall_progress REAL DEFAULT 0,
            learning_pace TEXT DEFAULT 'moderate',
            streak_days INTEGER DEFAULT 0,
            last_active DATE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            semester INTEGER NOT NULL,
            description TEXT,
            total_topics INTEGER DEFAULT 0
        )
    ''')
    
    # Topics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            difficulty TEXT DEFAULT 'beginner',
            order_index INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    # User progress tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            completion_status TEXT DEFAULT 'not_started',
            score REAL DEFAULT 0,
            time_spent INTEGER DEFAULT 0,
            last_accessed TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (topic_id) REFERENCES topics (id)
        )
    ''')
    
    # Quiz results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            score REAL NOT NULL,
            total_questions INTEGER,
            time_taken INTEGER,
            accuracy REAL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (topic_id) REFERENCES topics (id)
        )
    ''')
    
    # Learning resources
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            language TEXT DEFAULT 'english',
            difficulty TEXT,
            FOREIGN KEY (topic_id) REFERENCES topics (id)
        )
    ''')
    
    # Bookmarks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (resource_id) REFERENCES learning_resources (id)
        )
    ''')
    
    conn.commit()
    
    # Insert sample data
    insert_sample_data(conn)
    
    conn.close()

def insert_sample_data(conn):
    """Insert sample subjects, topics, and resources"""
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM subjects')
    if cursor.fetchone()[0] > 0:
        return
    
    # Sample subjects for different semesters
    subjects_data = [
        # Semester 1
        ('Programming in C', 1, 'Introduction to programming fundamentals', 15),
        ('Mathematics-I', 1, 'Engineering Mathematics basics', 12),
        ('Physics', 1, 'Applied Physics for Engineers', 10),
        
        # Semester 2
        ('Data Structures', 2, 'Arrays, Linked Lists, Trees, Graphs', 18),
        ('Object Oriented Programming (Java)', 2, 'OOP concepts with Java', 16),
        ('Mathematics-II', 2, 'Advanced Engineering Mathematics', 12),
        
        # Semester 3
        ('Database Management Systems', 3, 'SQL, Normalization, Transactions', 20),
        ('Operating Systems', 3, 'Process, Memory, File Management', 18),
        ('Computer Networks', 3, 'Network Protocols and Architecture', 16),
        ('Discrete Mathematics', 3, 'Logic, Sets, Graph Theory', 14),
        
        # Semester 4
        ('Design and Analysis of Algorithms', 4, 'Algorithm Design Techniques', 20),
        ('Web Technologies', 4, 'HTML, CSS, JavaScript, React', 22),
        ('Software Engineering', 4, 'SDLC, Design Patterns', 15),
        
        # Semester 5
        ('Artificial Intelligence', 5, 'Search, Logic, Machine Learning', 20),
        ('Machine Learning', 5, 'Supervised and Unsupervised Learning', 18),
        ('Compiler Design', 5, 'Lexical Analysis, Parsing', 16),
        
        # Semester 6
        ('Deep Learning', 6, 'Neural Networks, CNN, RNN', 20),
        ('Cloud Computing', 6, 'AWS, Azure, Docker, Kubernetes', 18),
        ('Cyber Security', 6, 'Cryptography, Network Security', 16),
        
        # Semester 7
        ('Natural Language Processing', 7, 'Text Processing, Transformers', 18),
        ('Big Data Analytics', 7, 'Hadoop, Spark, NoSQL', 16),
        ('Internet of Things', 7, 'IoT Architecture, Sensors', 14),
        
        # Semester 8
        ('Blockchain Technology', 8, 'Distributed Ledger, Smart Contracts', 15),
        ('Quantum Computing', 8, 'Quantum Gates, Algorithms', 12),
    ]
    
    cursor.executemany('''
        INSERT INTO subjects (name, semester, description, total_topics)
        VALUES (?, ?, ?, ?)
    ''', subjects_data)
    
    # Sample topics for a few subjects
    topics_data = [
        # Java topics (subject_id = 5)
        (5, 'Introduction to Java', 'Java basics, JVM, JDK', 'beginner', 1),
        (5, 'Classes and Objects', 'OOP fundamentals', 'beginner', 2),
        (5, 'Inheritance', 'Extends, super keyword', 'intermediate', 3),
        (5, 'Polymorphism', 'Method overloading and overriding', 'intermediate', 4),
        (5, 'Abstraction', 'Abstract classes and interfaces', 'intermediate', 5),
        (5, 'Exception Handling', 'Try-catch, throw, throws', 'intermediate', 6),
        (5, 'Collections Framework', 'List, Set, Map interfaces', 'advanced', 7),
        (5, 'Multithreading', 'Thread creation and synchronization', 'advanced', 8),
        
        # DBMS topics (subject_id = 7)
        (7, 'Introduction to DBMS', 'Database concepts', 'beginner', 1),
        (7, 'ER Model', 'Entity-Relationship diagrams', 'beginner', 2),
        (7, 'Relational Model', 'Tables, keys, relationships', 'beginner', 3),
        (7, 'SQL Basics', 'SELECT, INSERT, UPDATE, DELETE', 'beginner', 4),
        (7, 'SQL Joins', 'Inner, outer, cross joins', 'intermediate', 5),
        (7, 'Normalization', '1NF, 2NF, 3NF, BCNF', 'intermediate', 6),
        (7, 'Transactions', 'ACID properties', 'advanced', 7),
        (7, 'Indexing', 'B-trees, hashing', 'advanced', 8),
        
        # Web Technologies topics (subject_id = 12)
        (12, 'HTML Fundamentals', 'Tags, attributes, semantic HTML', 'beginner', 1),
        (12, 'CSS Basics', 'Selectors, box model, flexbox', 'beginner', 2),
        (12, 'CSS Grid', 'Grid layout system', 'intermediate', 3),
        (12, 'JavaScript Basics', 'Variables, functions, DOM', 'beginner', 4),
        (12, 'ES6 Features', 'Arrow functions, promises, async/await', 'intermediate', 5),
        (12, 'React Fundamentals', 'Components, props, state', 'intermediate', 6),
        (12, 'React Hooks', 'useState, useEffect, custom hooks', 'advanced', 7),
        (12, 'REST APIs', 'HTTP methods, fetch, axios', 'intermediate', 8),
    ]
    
    cursor.executemany('''
        INSERT INTO topics (subject_id, name, description, difficulty, order_index)
        VALUES (?, ?, ?, ?, ?)
    ''', topics_data)
    
    # Sample learning resources
    resources_data = [
        # Java resources
        (1, 'video', 'Java Tutorial for Beginners', 'https://www.youtube.com/watch?v=eIrMbAQSU34', 'english', 'beginner'),
        (1, 'article', 'Introduction to Java Programming', 'https://www.javatpoint.com/java-tutorial', 'english', 'beginner'),
        (2, 'video', 'Java OOP Concepts', 'https://www.youtube.com/watch?v=6T_HgnjoYwM', 'english', 'beginner'),
        (3, 'video', 'Inheritance in Java', 'https://www.youtube.com/watch?v=9JpNY-XAseg', 'english', 'intermediate'),
        (4, 'video', 'Polymorphism Explained', 'https://www.youtube.com/watch?v=jhDUxynEQRI', 'english', 'intermediate'),
        
        # DBMS resources
        (9, 'video', 'DBMS Complete Course', 'https://www.youtube.com/watch?v=c5HAwKX-suM', 'english', 'beginner'),
        (10, 'video', 'ER Diagrams Tutorial', 'https://www.youtube.com/watch?v=QpdhBUYk7Kk', 'english', 'beginner'),
        (12, 'video', 'SQL Tutorial - Full Course', 'https://www.youtube.com/watch?v=HXV3zeQKqGY', 'english', 'beginner'),
        (13, 'video', 'SQL Joins Explained', 'https://www.youtube.com/watch?v=9yeOJ0ZMUYw', 'english', 'intermediate'),
        
        # Web Technologies resources
        (17, 'video', 'HTML Full Course', 'https://www.youtube.com/watch?v=pQN-pnXPaVg', 'english', 'beginner'),
        (18, 'video', 'CSS Complete Tutorial', 'https://www.youtube.com/watch?v=1Rs2ND1ryYc', 'english', 'beginner'),
        (20, 'video', 'JavaScript Tutorial for Beginners', 'https://www.youtube.com/watch?v=W6NZfCO5SIk', 'english', 'beginner'),
        (22, 'video', 'React JS Full Course', 'https://www.youtube.com/watch?v=bMknfKXIFA8', 'english', 'intermediate'),
    ]
    
    cursor.executemany('''
        INSERT INTO learning_resources (topic_id, type, title, url, language, difficulty)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', resources_data)
    
    conn.commit()

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert user
        cursor.execute('''
            INSERT INTO users (username, password, email)
            VALUES (?, ?, ?)
        ''', (username, hashed_password, email))
        
        user_id = cursor.lastrowid
        
        # Create student profile
        cursor.execute('''
            INSERT INTO student_profiles (user_id, current_semester, last_active)
            VALUES (?, 1, DATE('now'))
        ''', (user_id,))
        
        conn.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'user_id': user_id
        }), 201
        
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            'message': 'Login successful',
            'user_id': user['id'],
            'username': user['username']
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

# ==================== DASHBOARD & PROFILE ROUTES ====================

@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile and progress"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT sp.*, u.username, u.email
        FROM student_profiles sp
        JOIN users u ON sp.user_id = u.id
        WHERE sp.user_id = ?
    ''', (user_id,))
    
    profile = dict(cursor.fetchone())
    
    # Get overall statistics
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT up.topic_id) as completed_topics,
            AVG(up.score) as avg_score,
            SUM(up.time_spent) as total_time
        FROM user_progress up
        WHERE up.user_id = ? AND up.completion_status = 'completed'
    ''', (user_id,))
    
    stats = dict(cursor.fetchone())
    profile.update(stats)
    
    conn.close()
    
    return jsonify(profile), 200

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    """Update user profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE student_profiles
        SET current_semester = ?, last_active = DATE('now')
        WHERE user_id = ?
    ''', (data.get('semester', 1), user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Profile updated'}), 200

# ==================== SUBJECT & TOPIC ROUTES ====================

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get subjects by semester"""
    semester = request.args.get('semester', type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    if semester:
        cursor.execute('''
            SELECT * FROM subjects WHERE semester = ? ORDER BY name
        ''', (semester,))
    else:
        cursor.execute('SELECT * FROM subjects ORDER BY semester, name')
    
    subjects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(subjects), 200

@app.route('/api/subjects/<int:subject_id>/topics', methods=['GET'])
def get_topics(subject_id):
    """Get topics for a subject"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, 
            COALESCE(up.completion_status, 'not_started') as user_status,
            COALESCE(up.score, 0) as user_score
        FROM topics t
        LEFT JOIN user_progress up ON t.id = up.topic_id 
            AND up.user_id = ?
        WHERE t.subject_id = ?
        ORDER BY t.order_index
    ''', (session.get('user_id', 0), subject_id))
    
    topics = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(topics), 200

@app.route('/api/topics/<int:topic_id>', methods=['GET'])
def get_topic_details(topic_id):
    """Get detailed topic information"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, s.name as subject_name, s.semester
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.id = ?
    ''', (topic_id,))
    
    topic = dict(cursor.fetchone())
    
    # Get user progress
    if 'user_id' in session:
        cursor.execute('''
            SELECT * FROM user_progress
            WHERE user_id = ? AND topic_id = ?
        ''', (session['user_id'], topic_id))
        
        progress = cursor.fetchone()
        if progress:
            topic['progress'] = dict(progress)
    
    conn.close()
    
    return jsonify(topic), 200

# ==================== LEARNING RESOURCES ROUTES ====================

@app.route('/api/topics/<int:topic_id>/resources', methods=['GET'])
def get_resources(topic_id):
    """Get learning resources for a topic"""
    language = request.args.get('language', 'english')
    resource_type = request.args.get('type')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT * FROM learning_resources
        WHERE topic_id = ? AND language = ?
    '''
    params = [topic_id, language]
    
    if resource_type:
        query += ' AND type = ?'
        params.append(resource_type)
    
    cursor.execute(query, params)
    resources = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(resources), 200

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized learning recommendations"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    # Get weak areas (topics with low scores)
    cursor.execute('''
        SELECT t.*, s.name as subject_name, up.score, up.completion_status
        FROM user_progress up
        JOIN topics t ON up.topic_id = t.id
        JOIN subjects s ON t.subject_id = s.id
        WHERE up.user_id = ? AND up.score < 70
        ORDER BY up.score ASC
        LIMIT 5
    ''', (user_id,))
    
    weak_areas = [dict(row) for row in cursor.fetchall()]
    
    # Get recommended next topics
    cursor.execute('''
        SELECT t.*, s.name as subject_name, s.semester
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ?
        WHERE up.id IS NULL OR up.completion_status != 'completed'
        ORDER BY t.order_index
        LIMIT 5
    ''', (user_id,))
    
    next_topics = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'weak_areas': weak_areas,
        'next_topics': next_topics,
        'recommendations': generate_ai_recommendations(weak_areas, next_topics)
    }), 200

def generate_ai_recommendations(weak_areas, next_topics):
    """Generate AI-based recommendations"""
    recommendations = []
    
    if weak_areas:
        recommendations.append({
            'type': 'revision',
            'priority': 'high',
            'message': f'Focus on revising {len(weak_areas)} weak topics to strengthen fundamentals'
        })
    
    if next_topics:
        recommendations.append({
            'type': 'progress',
            'priority': 'medium',
            'message': f'Continue learning with {next_topics[0]["name"]} in {next_topics[0]["subject_name"]}'
        })
    
    recommendations.append({
        'type': 'practice',
        'priority': 'medium',
        'message': 'Take more quizzes to improve retention and identify knowledge gaps'
    })
    
    return recommendations

# ==================== PROGRESS TRACKING ROUTES ====================

@app.route('/api/progress/update', methods=['POST'])
def update_progress():
    """Update learning progress for a topic"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.json
    topic_id = data.get('topic_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if progress exists
    cursor.execute('''
        SELECT id FROM user_progress
        WHERE user_id = ? AND topic_id = ?
    ''', (user_id, topic_id))
    
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE user_progress
            SET completion_status = ?,
                time_spent = time_spent + ?,
                last_accessed = CURRENT_TIMESTAMP
            WHERE user_id = ? AND topic_id = ?
        ''', (data.get('status', 'in_progress'),
              data.get('time_spent', 0),
              user_id, topic_id))
    else:
        cursor.execute('''
            INSERT INTO user_progress (user_id, topic_id, completion_status, time_spent, last_accessed)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, topic_id, data.get('status', 'in_progress'), data.get('time_spent', 0)))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Progress updated'}), 200

@app.route('/api/progress/analytics', methods=['GET'])
def get_analytics():
    """Get detailed analytics and performance data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    # Overall progress by subject
    cursor.execute('''
        SELECT 
            s.name as subject,
            COUNT(DISTINCT t.id) as total_topics,
            COUNT(DISTINCT CASE WHEN up.completion_status = 'completed' THEN up.topic_id END) as completed,
            AVG(CASE WHEN up.score > 0 THEN up.score ELSE NULL END) as avg_score
        FROM subjects s
        JOIN topics t ON s.id = t.subject_id
        LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ?
        GROUP BY s.id, s.name
        ORDER BY s.semester
    ''', (user_id,))
    
    subject_progress = [dict(row) for row in cursor.fetchall()]
    
    # Recent quiz results
    cursor.execute('''
        SELECT qr.*, t.name as topic_name, s.name as subject_name
        FROM quiz_results qr
        JOIN topics t ON qr.topic_id = t.id
        JOIN subjects s ON t.subject_id = s.id
        WHERE qr.user_id = ?
        ORDER BY qr.completed_at DESC
        LIMIT 10
    ''', (user_id,))
    
    recent_quizzes = [dict(row) for row in cursor.fetchall()]
    
    # Performance trend (last 30 days)
    cursor.execute('''
        SELECT 
            DATE(completed_at) as date,
            AVG(score) as avg_score,
            COUNT(*) as quiz_count
        FROM quiz_results
        WHERE user_id = ? AND completed_at >= DATE('now', '-30 days')
        GROUP BY DATE(completed_at)
        ORDER BY date
    ''', (user_id,))
    
    performance_trend = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'subject_progress': subject_progress,
        'recent_quizzes': recent_quizzes,
        'performance_trend': performance_trend
    }), 200

# ==================== QUIZ ROUTES ====================

@app.route('/api/quiz/<int:topic_id>', methods=['GET'])
def get_quiz(topic_id):
    """Generate quiz questions for a topic"""
    # In a real application, questions would be stored in database
    # For demo, generating sample questions
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, s.name as subject_name
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.id = ?
    ''', (topic_id,))
    
    topic = dict(cursor.fetchone())
    conn.close()
    
    # Generate sample quiz based on difficulty
    difficulty = topic['difficulty']
    num_questions = 10 if difficulty == 'beginner' else 15 if difficulty == 'intermediate' else 20
    
    quiz = {
        'topic_id': topic_id,
        'topic_name': topic['name'],
        'subject': topic['subject_name'],
        'difficulty': difficulty,
        'time_limit': num_questions * 60,  # 1 minute per question
        'questions': generate_sample_questions(topic, num_questions)
    }
    
    return jsonify(quiz), 200

def generate_sample_questions(topic, num_questions):
    """Generate sample quiz questions"""
    # Sample questions - in production, these would come from database
    question_templates = [
        {
            'question': f'What is the primary concept of {topic["name"]}?',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct': 0
        },
        {
            'question': f'Which statement about {topic["name"]} is true?',
            'options': ['Statement 1', 'Statement 2', 'Statement 3', 'Statement 4'],
            'correct': 1
        },
        {
            'question': f'How does {topic["name"]} work?',
            'options': ['Method A', 'Method B', 'Method C', 'Method D'],
            'correct': 2
        }
    ]
    
    questions = []
    for i in range(num_questions):
        template = question_templates[i % len(question_templates)]
        questions.append({
            'id': i + 1,
            'question': template['question'] + f' (Q{i+1})',
            'options': template['options'],
            'correct_answer': template['correct']
        })
    
    return questions

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz and calculate results"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.json
    
    topic_id = data['topic_id']
    answers = data['answers']
    time_taken = data['time_taken']
    total_questions = len(answers)
    
    # Calculate score (simplified - in production, validate against stored answers)
    correct = sum(1 for ans in answers if ans.get('is_correct', False))
    score = (correct / total_questions) * 100
    accuracy = score
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Save quiz result
    cursor.execute('''
        INSERT INTO quiz_results (user_id, topic_id, score, total_questions, time_taken, accuracy)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, topic_id, score, total_questions, time_taken, accuracy))
    
    # Update user progress
    cursor.execute('''
        INSERT OR REPLACE INTO user_progress (user_id, topic_id, completion_status, score, last_accessed)
        VALUES (?, ?, 'completed', ?, CURRENT_TIMESTAMP)
    ''', (user_id, topic_id, score))
    
    conn.commit()
    
    # Get analysis
    cursor.execute('''
        SELECT AVG(score) as avg_score, COUNT(*) as attempt_count
        FROM quiz_results
        WHERE user_id = ? AND topic_id = ?
    ''', (user_id, topic_id))
    
    stats = dict(cursor.fetchone())
    conn.close()
    
    result = {
        'score': score,
        'correct_answers': correct,
        'total_questions': total_questions,
        'accuracy': accuracy,
        'time_taken': time_taken,
        'performance': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Needs Improvement',
        'average_score': stats['avg_score'],
        'attempt_count': stats['attempt_count']
    }
    
    return jsonify(result), 200

# ==================== BOOKMARKS ROUTES ====================

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    """Get user's bookmarked resources"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT lr.*, t.name as topic_name, s.name as subject_name, b.created_at
        FROM bookmarks b
        JOIN learning_resources lr ON b.resource_id = lr.id
        JOIN topics t ON lr.topic_id = t.id
        JOIN subjects s ON t.subject_id = s.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    ''', (user_id,))
    
    bookmarks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(bookmarks), 200

@app.route('/api/bookmarks/add', methods=['POST'])
def add_bookmark():
    """Add a bookmark"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    resource_id = request.json.get('resource_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO bookmarks (user_id, resource_id)
            VALUES (?, ?)
        ''', (user_id, resource_id))
        conn.commit()
        return jsonify({'message': 'Bookmark added'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Already bookmarked'}), 200
    finally:
        conn.close()

@app.route('/api/bookmarks/remove/<int:bookmark_id>', methods=['DELETE'])
def remove_bookmark(bookmark_id):
    """Remove a bookmark"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM bookmarks
        WHERE id = ? AND user_id = ?
    ''', (bookmark_id, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Bookmark removed'}), 200

# ==================== MAIN ====================

if __name__ == '__main__':
    # Initialize database
    if not os.path.exists(DATABASE):
        init_db()
        print("Database initialized with sample data")
    
    print("Starting Personalized Learning Path Agent...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
