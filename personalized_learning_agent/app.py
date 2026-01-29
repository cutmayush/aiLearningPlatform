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
    # Note: Existence check removed here to allow forced re-initialization from main
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
    insert_sample_data(conn)
    conn.close()

def insert_sample_data(conn):
    """Insert sample subjects, topics, and resources with Dynamic IDs"""
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM subjects')
    if cursor.fetchone()[0] > 0:
        return
    
    print("Inserting sample data...")

    # 1. Insert Subjects
    subjects_data = [
        ('Programming in C', 1, 'Introduction to programming fundamentals', 15),
        ('Mathematics-I', 1, 'Engineering Mathematics basics', 12),
        ('Physics', 1, 'Applied Physics for Engineers', 10),
        ('Data Structures', 2, 'Arrays, Linked Lists, Trees, Graphs', 18),
        ('Object Oriented Programming (Java)', 2, 'OOP concepts with Java', 16),
        ('Mathematics-II', 2, 'Advanced Engineering Mathematics', 12),
        ('Database Management Systems', 3, 'SQL, Normalization, Transactions', 20),
        ('Operating Systems', 3, 'Process, Memory, File Management', 18),
        ('Computer Networks', 3, 'Network Protocols and Architecture', 16),
        ('Discrete Mathematics', 3, 'Logic, Sets, Graph Theory', 14),
        ('Design and Analysis of Algorithms', 4, 'Algorithm Design Techniques', 20),
        ('Web Technologies', 4, 'HTML, CSS, JavaScript, React', 22),
        ('Software Engineering', 4, 'SDLC, Design Patterns', 15),
        ('Artificial Intelligence', 5, 'Search, Logic, Machine Learning', 20),
        ('Machine Learning', 5, 'Supervised and Unsupervised Learning', 18),
        ('Compiler Design', 5, 'Lexical Analysis, Parsing', 16),
        ('Deep Learning', 6, 'Neural Networks, CNN, RNN', 20),
        ('Cloud Computing', 6, 'AWS, Azure, Docker, Kubernetes', 18),
        ('Cyber Security', 6, 'Cryptography, Network Security', 16),
        ('Natural Language Processing', 7, 'Text Processing, Transformers', 18),
        ('Big Data Analytics', 7, 'Hadoop, Spark, NoSQL', 16),
        ('Internet of Things', 7, 'IoT Architecture, Sensors', 14),
        ('Blockchain Technology', 8, 'Distributed Ledger, Smart Contracts', 15),
        ('Quantum Computing', 8, 'Quantum Gates, Algorithms', 12),
    ]
    cursor.executemany('INSERT INTO subjects (name, semester, description, total_topics) VALUES (?, ?, ?, ?)', subjects_data)
    
    # Helper to get Subject ID by Name
    def get_id(name):
        cursor.execute('SELECT id FROM subjects WHERE name = ?', (name,))
        res = cursor.fetchone()
        return res['id'] if res else None

    # Get IDs for subjects we want to populate
    math_id = get_id('Mathematics-I')
    phy_id = get_id('Physics')
    c_id = get_id('Programming in C')
    java_id = get_id('Object Oriented Programming (Java)')
    dbms_id = get_id('Database Management Systems')
    web_id = get_id('Web Technologies')

    # 2. Insert Topics
    topics_data = []
    
    # Mathematics-I Topics
    if math_id:
        topics_data.extend([
            (math_id, 'Matrices', 'Types of matrices, Rank, Inverse', 'beginner', 1),
            (math_id, 'Calculus', 'Limits, Continuity, Differentiation', 'intermediate', 2),
            (math_id, 'Differential Equations', 'First order and higher order', 'advanced', 3)
        ])

    # Physics Topics
    if phy_id:
        topics_data.extend([
            (phy_id, 'Quantum Mechanics', 'Wave-particle duality, Schrodinger equation', 'advanced', 1),
            (phy_id, 'Optics', 'Interference, Diffraction, Polarization', 'intermediate', 2),
            (phy_id, 'Electromagnetism', 'Maxwell equations, EM waves', 'intermediate', 3)
        ])

    # C Programming Topics
    if c_id:
        topics_data.extend([
            (c_id, 'Introduction to C', 'Variables, Data Types, Operators', 'beginner', 1),
            (c_id, 'Control Structures', 'If-else, Loops (for, while)', 'beginner', 2),
            (c_id, 'Arrays and Strings', '1D/2D Arrays, String handling', 'intermediate', 3),
            (c_id, 'Pointers', 'Pointer arithmetic, Memory management', 'advanced', 4)
        ])
        
    # Java Topics
    if java_id:
        topics_data.extend([
            (java_id, 'Java Basics', 'JVM, JRE, Syntax', 'beginner', 1),
            (java_id, 'OOP Concepts', 'Classes, Objects, Inheritance', 'intermediate', 2),
            (java_id, 'Collections', 'List, Set, Map', 'advanced', 3)
        ])

    # DBMS Topics
    if dbms_id:
        topics_data.extend([
            (dbms_id, 'Introduction to DBMS', 'Database concepts', 'beginner', 1),
            (dbms_id, 'SQL Basics', 'SELECT, INSERT, UPDATE', 'intermediate', 2)
        ])
        
    # Web Tech Topics
    if web_id:
         topics_data.extend([
            (web_id, 'HTML/CSS', 'Structure and Style', 'beginner', 1),
            (web_id, 'JavaScript', 'DOM, ES6', 'intermediate', 2)
        ])

    cursor.executemany('INSERT INTO topics (subject_id, name, description, difficulty, order_index) VALUES (?, ?, ?, ?, ?)', topics_data)
    
    # 3. Insert Resources (Videos & Articles)
    def get_topic_id(topic_name):
        cursor.execute('SELECT id FROM topics WHERE name = ?', (topic_name,))
        res = cursor.fetchone()
        return res['id'] if res else None

    resources_data = []

    # Resources for C Programming
    t_c_intro = get_topic_id('Introduction to C')
    if t_c_intro:
        resources_data.extend([
            (t_c_intro, 'video', 'C Programming in One Shot', 'https://www.youtube.com/watch?v=irqbmMNs2Bo', 'english', 'beginner'),
            (t_c_intro, 'article', 'C Language GeeksforGeeks', 'https://www.geeksforgeeks.org/c-programming-language/', 'english', 'beginner')
        ])
        
    # Resources for Mathematics
    t_matrices = get_topic_id('Matrices')
    if t_matrices:
        resources_data.extend([
            (t_matrices, 'video', 'Matrices One Shot', 'https://www.youtube.com/watch?v=xyz123', 'english', 'beginner'),
            (t_matrices, 'article', 'Matrices Notes', 'https://www.mathsisfun.com/algebra/matrix-introduction.html', 'english', 'beginner')
        ])
        
    # Resources for Physics
    t_quantum = get_topic_id('Quantum Mechanics')
    if t_quantum:
        resources_data.extend([
            (t_quantum, 'video', 'Quantum Mechanics Basics', 'https://www.youtube.com/watch?v=example', 'english', 'advanced')
        ])

    # Resources for Java
    t_java = get_topic_id('Java Basics')
    if t_java:
         resources_data.extend([
            (t_java, 'video', 'Java Tutorial for Beginners', 'https://www.youtube.com/watch?v=eIrMbAQSU34', 'english', 'beginner')
        ])

    cursor.executemany('INSERT INTO learning_resources (topic_id, type, title, url, language, difficulty) VALUES (?, ?, ?, ?, ?, ?)', resources_data)

    conn.commit()
    print("Sample data inserted successfully!")

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
        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, hashed_password, email))
        user_id = cursor.lastrowid
        cursor.execute('INSERT INTO student_profiles (user_id, current_semester, last_active) VALUES (?, 1, DATE("now"))', (user_id,))
        conn.commit()
        return jsonify({'message': 'Registration successful', 'user_id': user_id}), 201
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
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'message': 'Login successful', 'user_id': user['id'], 'username': user['username']}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ==================== DASHBOARD & PROFILE ROUTES ====================

@app.route('/dashboard')
def dashboard():
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
    
    # 1. Get Basic Profile
    cursor.execute('''
        SELECT sp.*, u.username, u.email
        FROM student_profiles sp
        JOIN users u ON sp.user_id = u.id
        WHERE sp.user_id = ?
    ''', (user_id,))
    
    profile_row = cursor.fetchone()
    if not profile_row:
        conn.close()
        return jsonify({'error': 'Profile not found'}), 404
        
    profile = dict(profile_row)
    
    # 2. Get Statistics (with COALESCE to handle nulls)
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT up.topic_id) as completed_topics,
            COALESCE(AVG(up.score), 0) as avg_score,
            COALESCE(SUM(up.time_spent), 0) as total_time
        FROM user_progress up
        WHERE up.user_id = ? AND up.completion_status = 'completed'
    ''', (user_id,))
    
    stats_row = cursor.fetchone()
    stats = dict(stats_row) if stats_row else {}
    profile.update(stats)
    
    conn.close()
    return jsonify(profile), 200

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.json
    conn = get_db()
    conn.execute('UPDATE student_profiles SET current_semester = ?, last_active = DATE("now") WHERE user_id = ?', 
                (data.get('semester', 1), user_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Profile updated'}), 200

# ==================== SUBJECT & TOPIC ROUTES ====================

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get subjects by semester with PROGRESS count"""
    semester = request.args.get('semester', type=int)
    user_id = session.get('user_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT s.*,
        (SELECT COUNT(DISTINCT up.topic_id) 
         FROM user_progress up 
         JOIN topics t ON up.topic_id = t.id 
         WHERE t.subject_id = s.id AND up.user_id = ? AND up.completion_status = 'completed') as completed
        FROM subjects s
    '''
    params = [user_id]
    
    if semester:
        query += ' WHERE s.semester = ? ORDER BY s.name'
        params.append(semester)
    else:
        query += ' ORDER BY s.semester, s.name'
        
    cursor.execute(query, params)
    subjects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(subjects), 200

@app.route('/api/subjects/<int:subject_id>/topics', methods=['GET'])
def get_topics(subject_id):
    conn = get_db()
    cursor = conn.cursor()
    user_id = session.get('user_id', 0)
    
    cursor.execute('''
        SELECT t.*, 
            COALESCE(up.completion_status, 'not_started') as user_status,
            COALESCE(up.score, 0) as user_score
        FROM topics t
        LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ?
        WHERE t.subject_id = ?
        ORDER BY t.order_index
    ''', (user_id, subject_id))
    
    topics = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(topics), 200

@app.route('/api/topics/<int:topic_id>', methods=['GET'])
def get_topic_details(topic_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, s.name as subject_name, s.semester
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.id = ?
    ''', (topic_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Topic not found'}), 404
        
    topic = dict(row)
    
    if 'user_id' in session:
        cursor.execute('SELECT * FROM user_progress WHERE user_id = ? AND topic_id = ?', 
                      (session['user_id'], topic_id))
        progress = cursor.fetchone()
        if progress:
            topic['progress'] = dict(progress)
    
    conn.close()
    return jsonify(topic), 200

# ==================== LEARNING RESOURCES & RECOMMENDATIONS ====================

@app.route('/api/topics/<int:topic_id>/resources', methods=['GET'])
def get_resources(topic_id):
    language = request.args.get('language', 'english')
    resource_type = request.args.get('type')
    
    conn = get_db()
    query = 'SELECT * FROM learning_resources WHERE topic_id = ? AND language = ?'
    params = [topic_id, language]
    
    if resource_type:
        query += ' AND type = ?'
        params.append(resource_type)
    
    rows = conn.execute(query, params).fetchall()
    resources = [dict(row) for row in rows]
    conn.close()
    return jsonify(resources), 200

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    conn = get_db()
    
    # Weak areas
    weak_rows = conn.execute('''
        SELECT t.*, s.name as subject_name, up.score
        FROM user_progress up
        JOIN topics t ON up.topic_id = t.id
        JOIN subjects s ON t.subject_id = s.id
        WHERE up.user_id = ? AND up.score < 70
        ORDER BY up.score ASC LIMIT 5
    ''', (user_id,)).fetchall()
    weak_areas = [dict(row) for row in weak_rows]
    
    # Next topics
    next_rows = conn.execute('''
        SELECT t.*, s.name as subject_name, s.semester
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ?
        WHERE up.id IS NULL OR up.completion_status != 'completed'
        ORDER BY t.order_index LIMIT 5
    ''', (user_id,)).fetchall()
    next_topics = [dict(row) for row in next_rows]
    
    conn.close()
    
    return jsonify({
        'weak_areas': weak_areas,
        'next_topics': next_topics,
        'recommendations': generate_ai_recommendations(weak_areas, next_topics)
    }), 200

def generate_ai_recommendations(weak_areas, next_topics):
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

# ==================== PROGRESS & QUIZ ====================

@app.route('/api/progress/update', methods=['POST'])
def update_progress():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.json
    topic_id = data.get('topic_id')
    status = data.get('status', 'in_progress')
    time_spent = data.get('time_spent', 0)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM user_progress WHERE user_id = ? AND topic_id = ?', (user_id, topic_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE user_progress
            SET completion_status = ?, time_spent = time_spent + ?, last_accessed = CURRENT_TIMESTAMP
            WHERE user_id = ? AND topic_id = ?
        ''', (status, time_spent, user_id, topic_id))
    else:
        cursor.execute('''
            INSERT INTO user_progress (user_id, topic_id, completion_status, time_spent, last_accessed)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, topic_id, status, time_spent))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Progress updated'}), 200

@app.route('/api/progress/analytics', methods=['GET'])
def get_analytics():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    conn = get_db()
    
    # Subject progress
    subj_rows = conn.execute('''
        SELECT s.name as subject, COUNT(DISTINCT t.id) as total_topics,
               COUNT(DISTINCT CASE WHEN up.completion_status = 'completed' THEN up.topic_id END) as completed,
               AVG(CASE WHEN up.score > 0 THEN up.score ELSE NULL END) as avg_score
        FROM subjects s
        JOIN topics t ON s.id = t.subject_id
        LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ?
        GROUP BY s.id, s.name ORDER BY s.semester
    ''', (user_id,)).fetchall()
    
    # Recent quizzes
    quiz_rows = conn.execute('''
        SELECT qr.*, t.name as topic_name, s.name as subject_name
        FROM quiz_results qr
        JOIN topics t ON qr.topic_id = t.id
        JOIN subjects s ON t.subject_id = s.id
        WHERE qr.user_id = ? ORDER BY qr.completed_at DESC LIMIT 10
    ''', (user_id,)).fetchall()
    
    # Performance trend
    trend_rows = conn.execute('''
        SELECT DATE(completed_at) as date, AVG(score) as avg_score, COUNT(*) as quiz_count
        FROM quiz_results WHERE user_id = ? AND completed_at >= DATE('now', '-30 days')
        GROUP BY DATE(completed_at) ORDER BY date
    ''', (user_id,)).fetchall()
    
    conn.close()
    return jsonify({
        'subject_progress': [dict(r) for r in subj_rows],
        'recent_quizzes': [dict(r) for r in quiz_rows],
        'performance_trend': [dict(r) for r in trend_rows]
    }), 200

@app.route('/api/quiz/<int:topic_id>', methods=['GET'])
def get_quiz(topic_id):
    conn = get_db()
    row = conn.execute('SELECT t.*, s.name as subject_name FROM topics t JOIN subjects s ON t.subject_id = s.id WHERE t.id = ?', (topic_id,)).fetchone()
    conn.close()
    
    if not row: return jsonify({'error': 'Topic not found'}), 404
    
    topic = dict(row)
    difficulty = topic['difficulty']
    num_questions = 10 if difficulty == 'beginner' else 15 if difficulty == 'intermediate' else 20
    
    return jsonify({
        'topic_id': topic_id,
        'topic_name': topic['name'],
        'subject': topic['subject_name'],
        'difficulty': difficulty,
        'time_limit': num_questions * 60,
        'questions': generate_sample_questions(topic, num_questions)
    }), 200

def generate_sample_questions(topic, num_questions):
    question_templates = [
        {'q': f'What is the main purpose of {topic["name"]}?', 'o': ['A', 'B', 'C', 'D'], 'c': 0},
        {'q': f'Key feature of {topic["name"]} is?', 'o': ['X', 'Y', 'Z', 'W'], 'c': 1},
        {'q': f'Which is true about {topic["name"]}?', 'o': ['False', 'True', 'False', 'False'], 'c': 1}
    ]
    questions = []
    for i in range(num_questions):
        tmpl = question_templates[i % len(question_templates)]
        questions.append({
            'id': i + 1,
            'question': tmpl['q'],
            'options': tmpl['o'],
            'correct_answer': tmpl['c']
        })
    return questions

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.json
    topic_id = data['topic_id']
    answers = data['answers']
    time_taken = data['time_taken']
    
    # Calculate score
    total_q = len(answers)
    correct = sum(1 for a in answers if a.get('is_correct', False))
    score = (correct / total_q) * 100 if total_q > 0 else 0
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Save Result
    cursor.execute('''
        INSERT INTO quiz_results (user_id, topic_id, score, total_questions, time_taken, accuracy)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, topic_id, score, total_q, time_taken, score))
    
    # 2. Update Progress (Smart Update: Don't overwrite existing progress blindly)
    cursor.execute('SELECT id FROM user_progress WHERE user_id=? AND topic_id=?', (user_id, topic_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE user_progress 
            SET completion_status='completed', score=?, last_accessed=CURRENT_TIMESTAMP 
            WHERE user_id=? AND topic_id=?
        ''', (score, user_id, topic_id))
    else:
        cursor.execute('''
            INSERT INTO user_progress (user_id, topic_id, completion_status, score, last_accessed)
            VALUES (?, ?, 'completed', ?, CURRENT_TIMESTAMP)
        ''', (user_id, topic_id, score))
        
    conn.commit()
    
    # 3. Get average for this topic
    stats = conn.execute('SELECT AVG(score) as avg_score, COUNT(*) as attempt_count FROM quiz_results WHERE user_id=? AND topic_id=?', (user_id, topic_id)).fetchone()
    conn.close()
    
    return jsonify({
        'score': score,
        'correct_answers': correct,
        'total_questions': total_q,
        'accuracy': score,
        'time_taken': time_taken,
        'performance': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Needs Improvement',
        'average_score': stats['avg_score'],
        'attempt_count': stats['attempt_count']
    }), 200

# ==================== BOOKMARKS ====================

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    conn = get_db()
    rows = conn.execute('''
        SELECT lr.*, t.name as topic_name, s.name as subject_name 
        FROM bookmarks b
        JOIN learning_resources lr ON b.resource_id = lr.id
        JOIN topics t ON lr.topic_id = t.id
        JOIN subjects s ON t.subject_id = s.id
        WHERE b.user_id = ? ORDER BY b.created_at DESC
    ''', (session['user_id'],)).fetchall()
    data = [dict(r) for r in rows]
    conn.close()
    return jsonify(data), 200

@app.route('/api/bookmarks/add', methods=['POST'])
def add_bookmark():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    try:
        conn = get_db()
        conn.execute('INSERT INTO bookmarks (user_id, resource_id) VALUES (?, ?)', 
                    (session['user_id'], request.json.get('resource_id')))
        conn.commit()
        return jsonify({'message': 'Bookmark added'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Already bookmarked'}), 200
    finally:
        conn.close()

@app.route('/api/bookmarks/remove/<int:bookmark_id>', methods=['DELETE'])
def remove_bookmark(bookmark_id):
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    conn = get_db()
    conn.execute('DELETE FROM bookmarks WHERE id = ? AND user_id = ?', (bookmark_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Removed'}), 200

# ==================== MAIN (FORCE RESET) ====================

if __name__ == '__main__':
    # 1. Purana Database Force Delete karein (For Hackathon/Testing Only)
    if os.path.exists(DATABASE):
        try:
            os.remove(DATABASE)
            print("Purana database successfully delete kar diya gaya.")
        except Exception as e:
            print(f"Delete warning: {e}")

    # 2. Naya Database Initialize karein (Ensure Sample Data is Inserted)
    init_db()
    print("Naya database Mathematics, Physics aur sabhi subjects ke saath ban gaya hai!")
    
    print("Starting Personalized Learning Path Agent...")
    app.run(debug=True, host='0.0.0.0', port=5000)
