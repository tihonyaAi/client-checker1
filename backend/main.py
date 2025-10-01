from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel
import jwt
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# templates folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# JWT settings
SECRET_KEY = "replace_this_with_a_long_random_secret_if_needed"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# -------------------------
# Create users programmatically:
# - 35 manager accounts: W1500CR .. W1534CR (passwords G13000 .. G13034)
# - One admin account: aurum_admin / ADM!n2025 (admin=True)
# You can edit this block later if you want different names/passwords.
# -------------------------

fake_users = {}

# generate 35 manager accounts
start_num = 1500
count = 35
for i in range(count):
    num = start_num + i
    username = f"W{num}CR"
    password = f"G13{num}"  # e.g. G131500 for W1500CR
    # store plain password for simplicity (no bcrypt)
    fake_users[username] = {
        "username": username,
        "password": password,
        "history": [],
        "is_admin": False
    }

# keep older account if you want (optional) — example
# fake_users["W1499CR"] = {
#     "username": "W1499CR",
#     "password": "G12793",
#     "history": [],
#     "is_admin": False
# }

# add separate admin account
fake_users["aurum_admin"] = {
    "username": "aurum_admin",
    "password": "ADM!n2025",
    "history": [],
    "is_admin": True
}

# Global taken nicks and global history
taken_nicks = set()   # store lower() values
global_history = []   # list of entries: dicts with time/nickname/status/user

# -------------------------
# Utilities
# -------------------------
def authenticate_user(username: str, password: str):
    user = fake_users.get(username)
    if not user:
        return None
    if password != user.get("password"):
        return None
    return user

def create_access_token(username: str):
    to_encode = {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or username not in fake_users:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return fake_users[username]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# -------------------------
# Routes
# -------------------------

@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    token = create_access_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}

class NicknameRequest(BaseModel):
    nicknames: List[str]

@app.post("/check")
def check_nicknames(data: NicknameRequest, user=Depends(get_current_user)):
    results = []
    for nick in data.nicknames:
        nick_str = nick.strip()
        key = nick_str.lower()
        if key in taken_nicks:
            status_text = "Ник занят"
        else:
            status_text = "Не найдено"
            taken_nicks.add(key)
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nickname": nick_str,
            "status": status_text,
            "user": user["username"]
        }
        # append to user's personal history and global history
        user["history"].append(entry)
        global_history.append(entry)
        results.append({"nickname": nick_str, "status": status_text})
    return {"results": results}

@app.get("/history")
def get_history(user=Depends(get_current_user)):
    # Admin sees global history
    if user.get("is_admin"):
        sorted_history = sorted(global_history, key=lambda x: x["time"], reverse=True)
        return [
            f"{item['time']} — {item['user']} — {item['nickname']} — {item['status']}"
            for item in sorted_history
        ]
    # Normal user sees personal history only
    else:
        sorted_personal = sorted(user["history"], key=lambda x: x["time"], reverse=True)
        return [
            f"{item['time']} — {item['nickname']} — {item['status']}"
            for item in sorted_personal
        ]
