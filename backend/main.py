from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Шаблоны и сессии
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Простая база данных ников
client_db = {"vasya", "petya", "masha"}

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if request.session.get("user") != "admin":
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/check_client", response_class=HTMLResponse)
def check_client(request: Request, nickname: str = Form(...)):
    if request.session.get("user") != "admin":
        return RedirectResponse("/", status_code=302)
    
    result = nickname in client_db
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "result": result,
        "nickname": nickname
    })
