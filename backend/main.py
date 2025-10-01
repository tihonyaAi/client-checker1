from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import json, os
from datetime import datetime, timedelta
from typing import List

# ==== Настройки ====
SECRET_KEY = "supersecretkey"      # секретный ключ для JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

# ==== Файл хранения данных ====
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# ==== FastAPI ====
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==== Работа с JSON ====
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}, "taken_nicks": [], "history": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load_data()

# ==== Авторизация ====
def authenticate_user(username: str, password: str):
    if username in db["users"] and db["users"][username] == password:
        return {"username": username}
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in db["users"]:
            raise HTTPException(status_code=401, detail="Неавторизован")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")

# ==== Роуты ====
@app.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    """Вход в систему и выдача токена"""
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/check")
async def check_nickname(request: Request, current_user: str = Depends(get_current_user)):
    """Проверка ника"""
    body = await request.json()
    nicknames: List[str] = body.get("nicknames", [])
    results = []

    for nickname in nicknames:
        if nickname in db["taken_nicks"]:
            results.append({"nickname": nickname, "status": "Ник занят"})
        else:
            db["taken_nicks"].append(nickname)
            results.append({"nickname": nickname, "status": "Свободен"})

        # сохраняем историю
        db["history"].setdefault(current_user, []).append(f"{nickname} - {results[-1]['status']}")

    save_data(db)
    return {"results": results}

@app.get("/history")
async def get_history(current_user: str = Depends(get_current_user)):
    """История проверок: админ видит всех, обычные — только себя"""
    if current_user == "admin":
        return {"history": db["history"]}
    return {"history": db["history"].get(current_user, [])}

@app.get("/export")
def export_data():
    """Экспорт всех данных (для админа, либо отладки)"""
    return db
