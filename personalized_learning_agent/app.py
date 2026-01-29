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
import google.generativeai as genai  # Library import

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# ==================== GEMINI API CONFIGURATION ====================
# Yahan apni NEW API Key dalein
GENAI_API_KEY = "AIzaSyBh9AMk0QIk9pqNERkjtRwfLXtRnpZigQs"
genai.configure(api_key=GENAI_API_KEY)

# Use the latest Gemini Flash model
print("[DEBUG] Initializing Gemini API with gemini-2.5-flash")
model = genai.GenerativeModel('gemini-2.5-flash')

# Database configuration
DATABASE = 'learning_agent.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tables Creation
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, email TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, current_semester INTEGER NOT NULL, overall_progress REAL DEFAULT 0, learning_pace TEXT DEFAULT 'moderate', streak_days INTEGER DEFAULT 0, last_active DATE, FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, semester INTEGER NOT NULL, description TEXT, total_topics INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS topics (id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, difficulty TEXT DEFAULT 'beginner', order_index INTEGER, FOREIGN KEY (subject_id) REFERENCES subjects (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, topic_id INTEGER NOT NULL, completion_status TEXT DEFAULT 'not_started', score REAL DEFAULT 0, time_spent INTEGER DEFAULT 0, last_accessed TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (topic_id) REFERENCES topics (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_results (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, topic_id INTEGER NOT NULL, score REAL NOT NULL, total_questions INTEGER, time_taken INTEGER, accuracy REAL, completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (topic_id) REFERENCES topics (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS learning_resources (id INTEGER PRIMARY KEY AUTOINCREMENT, topic_id INTEGER NOT NULL, type TEXT NOT NULL, title TEXT NOT NULL, url TEXT NOT NULL, language TEXT DEFAULT 'english', difficulty TEXT, FOREIGN KEY (topic_id) REFERENCES topics (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, resource_id INTEGER NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (resource_id) REFERENCES learning_resources (id))''')
    
    conn.commit()
    insert_sample_data(conn)
    conn.close()

def insert_sample_data(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM subjects')
    if cursor.fetchone()[0] > 0: return
    
    print("Inserting comprehensive data for all semesters...")

    # 1. Insert All Subjects (Sem 1-8)
    subjects_data = [
        ('Programming in C', 1, 'Introduction to programming fundamentals', 15),
        ('Mathematics-I', 1, 'Calculus and Linear Algebra', 12),
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

    # 2. Comprehensive Topic Map
    all_topics = {
        'Programming in C': [('Introduction to C', 'Variables', 'beginner'), ('Control Structures', 'Loops', 'beginner'), ('Arrays & Strings', 'Memory', 'intermediate'), ('Pointers', 'Address', 'advanced')],
        'Mathematics-I': [('Matrices', 'Rank, Inverse', 'beginner'), ('Calculus', 'Differentiation', 'intermediate'), ('Vector Spaces', 'Basis', 'advanced')],
        'Physics': [('Quantum Mechanics', 'Schrodinger', 'advanced'), ('Optics', 'Interference', 'intermediate'), ('Semiconductors', 'Diodes', 'intermediate')],
        'Data Structures': [('Linked Lists', 'Singly, Doubly', 'beginner'), ('Stacks & Queues', 'LIFO, FIFO', 'beginner'), ('Trees', 'BST, AVL', 'intermediate'), ('Graphs', 'BFS, DFS', 'advanced')],
        'Object Oriented Programming (Java)': [('Java Basics', 'JVM', 'beginner'), ('OOP Principles', 'Inheritance', 'intermediate'), ('Exception Handling', 'Try-Catch', 'intermediate'), ('Multithreading', 'Threads', 'advanced')],
        'Database Management Systems': [('ER Modeling', 'Entities', 'beginner'), ('SQL Queries', 'Joins', 'intermediate'), ('Normalization', 'BCNF', 'advanced')],
        'Operating Systems': [('Process Management', 'Scheduling', 'intermediate'), ('Deadlocks', 'Prevention', 'advanced'), ('Memory Management', 'Paging', 'intermediate')],
        'Web Technologies': [('HTML5 & CSS3', 'Layouts', 'beginner'), ('JavaScript ES6', 'DOM', 'intermediate'), ('React.js', 'Components', 'advanced')],
        'Artificial Intelligence': [('Search Algorithms', 'BFS, A*', 'intermediate'), ('Knowledge Representation', 'Logic', 'advanced'), ('Game Playing', 'Minimax', 'advanced')],
        'Cloud Computing': [('Cloud Models', 'IaaS, SaaS', 'beginner'), ('Virtualization', 'VMs', 'intermediate'), ('AWS Essentials', 'EC2', 'advanced')],
        'Natural Language Processing': [('Text Preprocessing', 'Tokenization', 'beginner'), ('Word Embeddings', 'Word2Vec', 'intermediate'), ('Transformers', 'BERT', 'advanced')],
        'Blockchain Technology': [('Blockchain Basics', 'Hash', 'beginner'), ('Smart Contracts', 'Solidity', 'advanced'), ('Consensus', 'PoW', 'intermediate')]
    }

    topic_id_map = {} 
    for subj_name, topics in all_topics.items():
        cursor.execute('SELECT id FROM subjects WHERE name = ?', (subj_name,))
        res = cursor.fetchone()
        if not res: continue
        subj_id = res['id']
        for idx, (t_name, t_desc, t_diff) in enumerate(topics):
            cursor.execute('INSERT INTO topics (subject_id, name, description, difficulty, order_index) VALUES (?, ?, ?, ?, ?)', (subj_id, t_name, t_desc, t_diff, idx+1))
            topic_id_map[t_name] = cursor.lastrowid

    # 3. Resources
    resources_data = []
    for t_name, t_id in topic_id_map.items():
        resources_data.append((t_id, 'video', f'{t_name} - Video Tutorial', 'https://www.youtube.com/results?search_query=' + t_name.replace(' ', '+'), 'english', 'beginner'))
        resources_data.append((t_id, 'article', f'{t_name} - Study Notes', 'https://www.geeksforgeeks.org/' + t_name.replace(' ', '-').lower() + '/', 'english', 'intermediate'))

    cursor.executemany('INSERT INTO learning_resources (topic_id, type, title, url, language, difficulty) VALUES (?, ?, ?, ?, ?, ?)', resources_data)
    conn.commit()
    print("Comprehensive sample data inserted successfully!")

# ==================== AI HELPER FUNCTIONS ====================

def get_gemini_quiz(topic_name, subject_name, difficulty):
    """Generates 5 MCQs using Gemini API"""
    prompt = f"""Create 5 multiple-choice questions (MCQs) on '{topic_name}' for the subject '{subject_name}' at {difficulty} difficulty level.
Return ONLY a valid JSON array with this exact structure:
[
  {{"id": 1, "question": "...", "options": ["A", "B", "C", "D"], "correct_answer": 0}},
  {{"id": 2, "question": "...", "options": ["A", "B", "C", "D"], "correct_answer": 1}},
  ...
]
No markdown, no extra text, just the JSON array."""
    try:
        print(f"[DEBUG] Requesting quiz for: {topic_name}")
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"[DEBUG] Raw Gemini Response: {text[:200]}")
        
        # Clean up response
        text = text.replace('```json', '').replace('```', '').replace('json', '').strip()
        
        # Parse JSON
        questions = json.loads(text)
        print(f"[DEBUG] Successfully parsed {len(questions)} questions from Gemini")
        return questions
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed: {e}")
        print(f"[DEBUG] Response text: {text[:500]}")
        return None
    except Exception as e:
        print(f"[ERROR] Gemini API Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_gemini_recommendations(weak_areas_list, current_sem):
    """Generates recommendations using Gemini API"""
    topics_str = ", ".join([w['name'] for w in weak_areas_list])
    prompt = f"""A student in Semester {current_sem} is struggling with these topics: {topics_str}.
Provide exactly 3 specific, motivating recommendations.
Return ONLY a valid JSON array with this exact structure:
[
  {{"type": "revision", "priority": "high", "message": "..."}},
  {{"type": "practice", "priority": "medium", "message": "..."}},
  {{"type": "progress", "priority": "low", "message": "..."}}
]
No markdown, no extra text, just the JSON array."""
    try:
        print(f"[DEBUG] Requesting recommendations for weak areas: {topics_str}")
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"[DEBUG] Raw Gemini Recommendations Response: {text[:200]}")
        
        # Clean up response
        text = text.replace('```json', '').replace('```', '').replace('json', '').strip()
        
        # Parse JSON
        recommendations = json.loads(text)
        print(f"[DEBUG] Successfully parsed {len(recommendations)} recommendations from Gemini")
        return recommendations
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed for recommendations: {e}")
        print(f"[DEBUG] Response text: {text[:500]}")
        return None
    except Exception as e:
        print(f"[ERROR] Gemini Recommendations API Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username, password, email = data.get('username'), data.get('password'), data.get('email')
    if not username or not password: return jsonify({'error': 'Missing fields'}), 400
    conn = get_db()
    try:
        hashed_pw = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, hashed_pw, email))
        user_id = cursor.lastrowid
        cursor.execute('INSERT INTO student_profiles (user_id, current_semester, last_active) VALUES (?, 1, DATE("now"))', (user_id,))
        conn.commit()
        return jsonify({'message': 'Success', 'user_id': user_id}), 201
    except sqlite3.IntegrityError: return jsonify({'error': 'Username exists'}), 409
    finally: conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (data.get('username'),)).fetchone()
    conn.close()
    if user and check_password_hash(user['password'], data.get('password')):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'message': 'Success', 'user_id': user['id']}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session: return jsonify({'error': 'Auth failed'}), 401
    conn = get_db()
    profile = dict(conn.execute('SELECT sp.*, u.username FROM student_profiles sp JOIN users u ON sp.user_id = u.id WHERE u.id = ?', (session['user_id'],)).fetchone())
    stats = dict(conn.execute('SELECT COUNT(DISTINCT topic_id) as completed_topics, COALESCE(AVG(score),0) as avg_score, COALESCE(SUM(time_spent),0) as total_time FROM user_progress WHERE user_id = ? AND completion_status="completed"', (session['user_id'],)).fetchone())
    profile.update(stats)
    conn.close()
    return jsonify(profile)

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session: return jsonify({'error': 'Auth failed'}), 401
    conn = get_db()
    conn.execute('UPDATE student_profiles SET current_semester = ? WHERE user_id = ?', (request.json.get('semester'), session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Updated'})

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    sem = request.args.get('semester', type=int)
    user_id = session.get('user_id')
    conn = get_db()
    query = '''SELECT s.*, (SELECT COUNT(DISTINCT up.topic_id) FROM user_progress up JOIN topics t ON up.topic_id=t.id WHERE t.subject_id=s.id AND up.user_id=? AND up.completion_status='completed') as completed FROM subjects s'''
    params = [user_id]
    if sem:
        query += ' WHERE s.semester = ? ORDER BY s.name'
        params.append(sem)
    else:
        query += ' ORDER BY s.semester, s.name'
    subjects = [dict(row) for row in conn.execute(query, params).fetchall()]
    conn.close()
    return jsonify(subjects)

@app.route('/api/subjects/<int:subject_id>/topics', methods=['GET'])
def get_topics(subject_id):
    conn = get_db()
    topics = [dict(row) for row in conn.execute('''SELECT t.*, COALESCE(up.completion_status, 'not_started') as user_status, COALESCE(up.score, 0) as user_score FROM topics t LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ? WHERE t.subject_id = ? ORDER BY t.order_index''', (session.get('user_id'), subject_id)).fetchall()]
    conn.close()
    return jsonify(topics)

@app.route('/api/topics/<int:topic_id>/resources', methods=['GET'])
def get_resources(topic_id):
    conn = get_db()
    res = [dict(row) for row in conn.execute('SELECT * FROM learning_resources WHERE topic_id = ?', (topic_id,)).fetchall()]
    conn.close()
    return jsonify(res)

# ==================== AI-POWERED QUIZ ROUTE ====================
@app.route('/api/quiz/<int:topic_id>', methods=['GET'])
def get_quiz(topic_id):
    conn = get_db()
    topic = conn.execute('SELECT t.name, t.difficulty, s.name as subject FROM topics t JOIN subjects s ON t.subject_id=s.id WHERE t.id=?', (topic_id,)).fetchone()
    conn.close()
    
    if not topic: return jsonify({'error': 'Topic not found'}), 404
    
    # 1. Try Gemini API
    print(f"Generating AI Quiz for: {topic['name']}")
    questions = get_gemini_quiz(topic['name'], topic['subject'], topic['difficulty'])
    
    # 2. Fallback
    if not questions:
        print("Gemini API failed, using fallback.")
        questions = [
            {'id': 1, 'question': f'What is a core concept of {topic["name"]}?', 'options': ['Concept A', 'Concept B', 'Concept C', 'Concept D'], 'correct_answer': 0},
            {'id': 2, 'question': f'Why is {topic["name"]} important in {topic["subject"]}?', 'options': ['Reason X', 'Reason Y', 'Reason Z', 'Reason W'], 'correct_answer': 1},
            {'id': 3, 'question': f'Which tool is used in {topic["name"]}?', 'options': ['Tool 1', 'Tool 2', 'Tool 3', 'Tool 4'], 'correct_answer': 2},
            {'id': 4, 'question': f'True or False: {topic["name"]} is complex.', 'options': ['True', 'False', 'Depends', 'None'], 'correct_answer': 0},
            {'id': 5, 'question': f'Apply {topic["name"]} to a problem.', 'options': ['Sol 1', 'Sol 2', 'Sol 3', 'Sol 4'], 'correct_answer': 3},
        ]
    
    return jsonify({
        'topic_id': topic_id, 'topic_name': topic['name'], 'subject': topic['subject'], 'time_limit': 300, 'questions': questions
    })

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.json
    score = (sum(1 for a in data['answers'] if a.get('is_correct')) / len(data['answers'])) * 100
    conn = get_db()
    conn.execute('INSERT INTO quiz_results (user_id, topic_id, score, total_questions, time_taken, accuracy) VALUES (?,?,?,?,?,?)', (session['user_id'], data['topic_id'], score, len(data['answers']), data['time_taken'], score))
    conn.execute('INSERT OR REPLACE INTO user_progress (user_id, topic_id, completion_status, score, last_accessed) VALUES (?, ?, "completed", ?, CURRENT_TIMESTAMP)', (session['user_id'], data['topic_id'], score))
    conn.commit()
    conn.close()
    return jsonify({'score': score, 'performance': 'Good' if score > 60 else 'Needs Improvement'})

# ==================== AI-POWERED RECOMMENDATIONS ====================
@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    if 'user_id' not in session: return jsonify({'error': 'Auth failed'}), 401
    user_id = session['user_id']
    conn = get_db()
    
    prof = conn.execute('SELECT current_semester FROM student_profiles WHERE user_id=?', (user_id,)).fetchone()
    current_sem = prof['current_semester'] if prof else 1
    
    # Get Weak Areas
    weak_rows = conn.execute('SELECT t.name, s.name as subject_name, up.score FROM user_progress up JOIN topics t ON up.topic_id = t.id JOIN subjects s ON t.subject_id = s.id WHERE up.user_id = ? AND up.score < 60 ORDER BY up.score ASC LIMIT 3', (user_id,)).fetchall()
    weak_areas = [dict(r) for r in weak_rows]
    
    # Get Next Topics
    next_rows = conn.execute('SELECT t.*, s.name as subject_name, s.semester FROM topics t JOIN subjects s ON t.subject_id = s.id LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ? WHERE (up.id IS NULL OR up.completion_status != "completed") AND s.semester = ? ORDER BY t.order_index ASC LIMIT 5', (user_id, current_sem)).fetchall()
    next_topics = [dict(r) for r in next_rows]
    conn.close()
    
    # 1. Try Gemini Recommendations
    ai_recommendations = []
    if weak_areas:
        print("Generating AI Recommendations...")
        ai_recommendations = get_gemini_recommendations(weak_areas, current_sem)
    
    # 2. Fallback
    if not ai_recommendations:
        if weak_areas:
            t_names = ", ".join([w['name'] for w in weak_areas[:2]])
            ai_recommendations.append({'type': 'revision', 'priority': 'high', 'message': f"⚠️ Revision Alert: Scores in {t_names} are low. Please review."})
        
        if next_topics:
            top = next_topics[0]
            ai_recommendations.append({'type': 'progress', 'priority': 'medium', 'message': f"🚀 Recommended: Start {top['name']} from {top['subject_name']}."})
        else:
            ai_recommendations.append({'type': 'progress', 'priority': 'low', 'message': "🎉 All caught up for this semester!"})
            
        ai_recommendations.append({'type': 'practice', 'priority': 'low', 'message': "💡 Consistency is key! Keep learning."})
    
    return jsonify({'weak_areas': weak_areas, 'next_topics': next_topics, 'recommendations': ai_recommendations})

# ==================== ANALYTICS & BOOKMARKS ====================

@app.route('/api/progress/update', methods=['POST'])
def update_progress_tracking():
    if 'user_id' not in session: return jsonify({'error': 'Auth failed'}), 401
    user_id = session['user_id']
    data = request.json
    conn = get_db()
    conn.execute('INSERT OR REPLACE INTO user_progress (user_id, topic_id, completion_status, time_spent, last_accessed) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)', (user_id, data.get('topic_id'), data.get('status', 'in_progress'), data.get('time_spent', 0)))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Updated'})

@app.route('/api/progress/analytics', methods=['GET'])
def get_analytics():
    if 'user_id' not in session: return jsonify({'error': 'Auth failed'}), 401
    user_id = session['user_id']
    semester = request.args.get('semester', type=int)
    conn = get_db()
    
    if not semester:
        prof = conn.execute('SELECT current_semester FROM student_profiles WHERE user_id=?', (user_id,)).fetchone()
        semester = prof['current_semester'] if prof else 1

    subj_rows = conn.execute('''SELECT s.name as subject, COUNT(DISTINCT t.id) as total_topics, COUNT(DISTINCT CASE WHEN up.completion_status = 'completed' THEN up.topic_id END) as completed, AVG(CASE WHEN up.score > 0 THEN up.score ELSE NULL END) as avg_score FROM subjects s JOIN topics t ON s.id = t.subject_id LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ? WHERE s.semester = ? GROUP BY s.id, s.name''', (user_id, semester)).fetchall()
    
    sem_stats = conn.execute('''SELECT COALESCE(SUM(up.time_spent), 0) as semester_time, COUNT(DISTINCT t.id) as total_sem_topics, COUNT(DISTINCT CASE WHEN up.completion_status='completed' THEN up.topic_id END) as completed_sem_topics FROM subjects s JOIN topics t ON s.id = t.subject_id LEFT JOIN user_progress up ON t.id = up.topic_id AND up.user_id = ? WHERE s.semester = ?''', (user_id, semester)).fetchone()
    
    quiz_rows = conn.execute('''SELECT qr.*, t.name as topic_name, s.name as subject_name FROM quiz_results qr JOIN topics t ON qr.topic_id = t.id JOIN subjects s ON t.subject_id = s.id WHERE qr.user_id = ? AND s.semester = ? ORDER BY qr.completed_at DESC LIMIT 5''', (user_id, semester)).fetchall()
    
    trend_rows = conn.execute('''SELECT DATE(qr.completed_at) as date, AVG(qr.score) as avg_score FROM quiz_results qr JOIN topics t ON qr.topic_id = t.id JOIN subjects s ON t.subject_id = s.id WHERE qr.user_id = ? AND s.semester = ? GROUP BY DATE(qr.completed_at) ORDER BY date''', (user_id, semester)).fetchall()
    
    conn.close()
    return jsonify({
        'subject_progress': [dict(r) for r in subj_rows],
        'recent_quizzes': [dict(r) for r in quiz_rows],
        'performance_trend': [dict(r) for r in trend_rows],
        'semester_stats': {'total_time': sem_stats['semester_time'], 'total_topics': sem_stats['total_sem_topics'], 'completed_topics': sem_stats['completed_sem_topics']}
    })

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    conn = get_db()
    rows = conn.execute('''SELECT lr.*, t.name as topic_name, s.name as subject_name FROM bookmarks b JOIN learning_resources lr ON b.resource_id = lr.id JOIN topics t ON lr.topic_id = t.id JOIN subjects s ON t.subject_id = s.id WHERE b.user_id = ? ORDER BY b.created_at DESC''', (session['user_id'],)).fetchall()
    data = [dict(r) for r in rows]
    conn.close()
    return jsonify(data), 200

@app.route('/api/bookmarks/add', methods=['POST'])
def add_bookmark():
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    try:
        conn = get_db()
        conn.execute('INSERT INTO bookmarks (user_id, resource_id) VALUES (?, ?)', (session['user_id'], request.json.get('resource_id')))
        conn.commit()
        return jsonify({'message': 'Bookmark added'}), 201
    except sqlite3.IntegrityError: return jsonify({'message': 'Already bookmarked'}), 200
    finally: conn.close()

@app.route('/api/bookmarks/remove/<int:bookmark_id>', methods=['DELETE'])
def remove_bookmark(bookmark_id):
    if 'user_id' not in session: return jsonify({'error': 'Not authenticated'}), 401
    conn = get_db()
    conn.execute('DELETE FROM bookmarks WHERE id = ? AND user_id = ?', (bookmark_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Removed'}), 200

if __name__ == '__main__':
    # Force Reset Database
    if os.path.exists(DATABASE):
        try: os.remove(DATABASE)
        except: pass
    init_db()
    print("AI-Powered Learning Agent Ready!")
    app.run(debug=True, host='0.0.0.0', port=5000)
