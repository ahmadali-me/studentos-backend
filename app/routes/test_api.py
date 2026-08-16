import requests

API_KEY = "dummykey"

# Testing Gemini API directly
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print("\n-------------------------------------------")
print(f"STATUS CODE: {response.status_code}")
print(f"RAW RESPONSE: {response.text}")
print("-------------------------------------------\n")