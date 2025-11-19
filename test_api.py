import requests
import json

BASE_URL = "http://localhost:5000"

# Teste 1: Página inicial
print("=== Teste 1: Página Inicial ===")
response = requests.get(f"{BASE_URL}/")
print(response.json())
print()

# Teste 2: Params
print("=== Teste 2: Params ===")
response = requests.get(f"{BASE_URL}/api/params")
print(json.dumps(response.json(), indent=2))
print()

# Teste 3: Deploy
print("=== Teste 3: Deploy ===")
payload = {
    "inveniraStdID": "student_123",
    "idioma": "pt",
    "nivelInicial": 2
}
response = requests.post(f"{BASE_URL}/api/deploy", json=payload)
print(json.dumps(response.json(), indent=2))
print()

# Teste 4: Analytics List
print("=== Teste 4: Analytics List ===")
response = requests.get(f"{BASE_URL}/api/analytics-list")
print(json.dumps(response.json(), indent=2))
print()

# Teste 5: Analytics
print("=== Teste 5: Analytics ===")
payload = {"inveniraStdID": "student_123"}
response = requests.post(f"{BASE_URL}/api/analytics", json=payload)
print(json.dumps(response.json(), indent=2))