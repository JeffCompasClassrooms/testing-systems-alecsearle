import requests

response = requests.get("http://localhost:8080/squirrels")

print("Status code:", response.status_code)
print("Headers:", response.headers)
print("Body:", response.text[:200])
