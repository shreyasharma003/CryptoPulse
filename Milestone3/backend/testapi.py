import requests

url = "http://127.0.0.1:5000/signup"
data = {
    "fullName": "Test User",
    "email": "testuser@example.com",
    "password": "password123"
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())
