import json
import pytest
import tempfile
import os

import app as learning_app


@pytest.fixture(scope='module')
def test_client():
    # Use a temporary file SQLite DB for tests so connections share schema
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.close()
    db_path = tf.name
    learning_app.DATABASE = db_path
    learning_app.init_db()

    testing_client = learning_app.app.test_client()
    ctx = learning_app.app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()
    try:
        os.unlink(db_path)
    except Exception:
        pass


def test_register_login_and_recommendations(test_client):
    # Register
    resp = test_client.post('/register', json={'username': 'testuser', 'password': 'pass123', 'email': 't@t.com'})
    assert resp.status_code in (200, 201)

    # Login
    resp = test_client.post('/login', json={'username': 'testuser', 'password': 'pass123'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'user_id' in data

    # Set session cookie in client (Flask test_client handles session)
    # Update profile semester
    resp = test_client.post('/api/profile/update', json={'semester': 2})
    assert resp.status_code == 200

    # Get recommendations
    resp = test_client.get('/api/recommendations')
    assert resp.status_code == 200
    rec = resp.get_json()
    assert 'next_topics' in rec


def test_quiz_endpoint(test_client):
    # Ensure topic 1 exists from sample data
    resp = test_client.get('/api/quiz/1')
    # If not authenticated, endpoint still returns quiz (no auth required)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'questions' in data and isinstance(data['questions'], list)
