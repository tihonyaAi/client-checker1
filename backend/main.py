from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel
import jwt
import os

# === Создание приложения ===
app = FastAPI()

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === HTML шаблоны ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# === JWT настройки ===
SECRET_KEY = "replace_with_a_real_secret_key_in_prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 сутки

# === Пароли ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# === База пользователей ===
# W1499CR — основной аккаунт, имеет право смотреть всю глобальную историю (is_admin=True)
fake_users = {
    "W1499CR": {
        "username": "W1499CR",
        "hashed_password": pwd_context.hash("G12793"),
        "history": [],
        "is_admin": True
    },
    # Можно добавить других менеджеров здесь, для теста:
    "manager1": {
        "username": "manager1",
        "hashed_password": pwd_context.hash("pass1"),
        "history": [],
        "is_admin": False
    }
}

# === Глобальная база занятых ников ===
taken_nicks = set()           # храним lower() ников
global_history = []           # список всех записей: элементы — словари

# === Утилиты ===
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users.get(username)
    if user and verify_password(password, user["hashed_password"]):
        return user
    return None

def create_access_token(username: str):
    to_encode = {"sub": username}
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or username not in fake_users:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return fake_users[username]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# === Роуты ===

@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    access_token = create_access_token(form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}

class NicknameRequest(BaseModel):
    nicknames: List[str]

@app.post("/check")
def check_nicknames(data: NicknameRequest, user=Depends(get_current_user)):
    results = []
    for raw_nick in data.nicknames:
        nick = raw_nick.strip()
        key = nick.lower()
        if key in taken_nicks:
            status = "Ник занят"
        else:
            status = "Не найдено"
            taken_nicks.add(key)
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nickname": nick,
            "status": status,
            "user": user["username"]
        }
        # добавляем запись пользователю и в глобальную историю
        user["history"].append(entry)
        global_history.append(entry)
        results.append({"nickname": nick, "status": status})
    return {"results": results}

@app.get("/history")
def get_history(user=Depends(get_current_user)):
    # Если админ — вернуть полностью глобальную историю
    if user.get("is_admin"):
        sorted_history = sorted(global_history, key=lambda x: x["time"], reverse=True)
        return [
            f"{item['time']} — {item['user']} — {item['nickname']} — {item['status']}"
            for item in sorted_history
        ]
    # Иначе — только личную историю
    else:
        sorted_personal = sorted(user["history"], key=lambda x: x["time"], reverse=True)
        return [
            f"{item['time']} — {item['nickname']} — {item['status']}"
            for item in sorted_personal
        ]
