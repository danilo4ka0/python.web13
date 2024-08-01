import typing
from pydantic import BaseModel

import os
import sys


sys.path.append("C:/Users/demo/Desktop/python.web12")

try:
    from database import Base
    print("Импорт успешен!")
except ImportError as e:
    print(f"Ошибка импорта: {e}")


# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from redis import Redis
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, lambda request, exc: 
    JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content="Too many requests")
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    # Додайте інші дозволені джерела
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

class User(BaseModel):
    email: EmailStr
    is_verified: bool = False

class Contact(BaseModel):
    name: str
    email: EmailStr

users = []
contacts = []

@app.post("/register")
async def register(user: User):
    users.append(user)
    # Надіслати електронний лист для верифікації (тут потрібно інтегрувати з email сервісом)
    return {"msg": "Please verify your email"}

@app.get("/verify/{token}")
async def verify(token: str):
    # Розшифрувати і перевірити токен (тут потрібно інтегрувати з токен сервісом)
    for user in users:
        if user.email == decoded_email:
            user.is_verified = True
            return {"msg": "Email verified"}
    raise HTTPException(status_code=400, detail="Invalid token")

@app.post("/contact", dependencies=[Depends(limiter.limit("5/minute"))])
async def create_contact(contact: Contact):
    contacts.append(contact)
    return contact

@app.post("/upload-avatar")
async def upload_avatar(file: UploadFile):
    result = cloudinary.uploader.upload(file.file)
    url = result.get("secure_url")
    return {"url": url}

# Dockerfile
"""
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""

# docker-compose.yml
"""
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CLOUDINARY_CLOUD_NAME=${CLOUDINARY_CLOUD_NAME}
      - CLOUDINARY_API_KEY=${CLOUDINARY_API_KEY}
      - CLOUDINARY_API_SECRET=${CLOUDINARY_API_SECRET}
    volumes:
      - .:/app
    depends_on:
      - redis

  redis:
    image: "redis:latest"
    ports:
      - "6379:6379"
"""

# .env
"""
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
"""

# requirements.txt
"""
fastapi
uvicorn
slowapi
cloudinary
python-dotenv
redis
"""

# Виконання кешування з Redis
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/login")
async def login(user: User):
    # Перевірка користувача
    redis_client.set(f"user:{user.email}", user.json())
    return {"msg": "Logged in"}

@app.get("/current-user")
async def get_current_user(email: str):
    user_data = redis_client.get(f"user:{email}")
    if user_data:
        return json.loads(user_data)
    raise HTTPException(status_code=404, detail="User not found")

# Реалізація скидання паролю
@app.post("/reset-password")
async def reset_password(email: EmailStr):
    # Надіслати лист для скидання паролю (тут потрібно інтегрувати з email сервісом)
    return {"msg": "Check your email for reset instructions"}
