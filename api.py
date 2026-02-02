import requests

url = "https://notify.eskiz.uz/api/auth/login"
data = {
    "email": "ia1888980@gmail.com",
    "password": "FaeokndLJB6yfSrt"
}

res = requests.post(url, data=data)
print(res.json())
