import requests

BASE = 'http://127.0.0.1:5000'

s = requests.Session()
username = 'apitest_user'
password = 'testpass123'

# Try to register (ignore if already exists)
resp = s.post(f'{BASE}/register', json={'username': username, 'password': password, 'email': 'a@b.com'})
print('register:', resp.status_code, resp.json())

# Login
resp = s.post(f'{BASE}/login', json={'username': username, 'password': password})
print('login:', resp.status_code, resp.json())

# Optionally set semester to 2
resp = s.post(f'{BASE}/api/profile/update', json={'semester': 2})
print('update profile:', resp.status_code, resp.json())

# Get recommendations
resp = s.get(f'{BASE}/api/recommendations')
print('recommendations:', resp.status_code)
print(resp.json())
