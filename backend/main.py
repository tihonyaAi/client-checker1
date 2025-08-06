from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

app = FastAPI()

# Разрешаем все источники (для CORS)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройки для токенов
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Имитация базы данных
users_db = {}
clients_db = []

# Модели
class User(BaseModel):
    username: str
    password: str

class NicknameRequest(BaseModel):
    nicknames: List[str]

class NicknameResponse(BaseModel):
    results: List[dict]

class Token(BaseModel):
    access_token: str
    token_type: str

# Создание токена
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Получение текущего пользователя по токену
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Регистрация пользователя
@app.post("/register")
def register(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[user.username] = {
        "username": user.username,
        "password": pwd_context.hash(user.password),
        "nicknames": []
    }
    return {"message": "User registered"}

# Авторизация и получение токена
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Проверка никнеймов
@app.post("/check", response_model=NicknameResponse)
def check_nicknames(req: NicknameRequest, current_user: str = Depends(get_current_user)):
    results = []
    for nickname in req.nicknames:
        if any(nickname == entry["nickname"] for entry in clients_db):
            results.append({"nickname": nickname, "status": "❌"})
        else:
            clients_db.append({"nickname": nickname, "user": current_user})
            users_db[current_user]["nicknames"].append(nickname)
            results.append({"nickname": nickname, "status": "✅"})
    return {"results": results}

# Получение истории пользователя
@app.get("/history", response_model=List[str])
def get_history(current_user: str = Depends(get_current_user)):
    return users_db[current_user]["nicknames"]

# Добавим простой корень для проверки сервиса
@app.get("/")
def read_root():
    return {"status": "ok"}

# Точка входа для запуска сервера на Render
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
