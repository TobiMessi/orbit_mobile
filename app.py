from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from database import query_db, init_db
from docker_logic import get_docker_stats

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    init_db()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/register")
async def register(username: str = Form(...), password: str = Form(...)):
    try:
        exists = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
        if exists:
            return JSONResponse(status_code=400, content={"status": "error", "message": "User already exists"})

        query_db("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        return {"status": "success", "message": "Registration successful"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = query_db("SELECT * FROM users WHERE username = ? AND password = ?", (username, password), one=True)
    if user:
        return {"status": "success", "message": "Login successful"}
    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid credentials"})


@app.get("/api/stats")
async def stats():
    return get_docker_stats()


@app.get('/favicon.ico')
async def favicon():
    return FileResponse("static/img/logo.svg")