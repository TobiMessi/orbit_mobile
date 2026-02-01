from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import hashlib

from database import query_db, init_db, get_user_servers, add_server, set_active_server, get_active_server, delete_server
from docker_logic import get_docker_stats, container_action, stack_action, ping_server

app = FastAPI()
app.add_middleware(
    SessionMiddleware, 
    secret_key="orbit-super-secret-key-2024-fixed-permanent",
    session_cookie="orbit_session",
    max_age=60*60*24*30,
    same_site="lax",
    https_only=False
)

@app.on_event("startup")
async def startup_event():
    init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(request: Request):
    return request.session.get("user_id")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    user_id = get_current_user(request)
    if not user_id:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/register")
async def register(username: str = Form(...), password: str = Form(...)):
    try:
        exists = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
        if exists:
            return JSONResponse(status_code=400, content={"status": "error", "message": "User already exists"})

        hashed = hash_password(password)
        query_db("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        return {"status": "success", "message": "Registration successful"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    hashed = hash_password(password)
    user = query_db("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed), one=True)
    if user:
        request.session["user_id"] = user["id"]
        request.session["username"] = user["username"]
        return {"status": "success", "message": "Login successful"}
    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid credentials"})

@app.get("/api/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.post("/api/servers/add")
async def add_server_route(request: Request, name: str = Form(...), ip: str = Form(...), port: int = Form(5001)):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    add_server(user_id, name, ip, port)
    
    servers = get_user_servers(user_id)
    if len(servers) == 1:
        set_active_server(user_id, servers[0]["id"])
    
    return {"status": "success", "message": "Server added"}

@app.post("/api/servers/{server_id}/activate")
async def activate_server(request: Request, server_id: int):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    set_active_server(user_id, server_id)
    return {"status": "success", "message": "Server activated"}

@app.delete("/api/servers/{server_id}")
async def remove_server(request: Request, server_id: int):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    delete_server(server_id, user_id)
    return {"status": "success", "message": "Server removed"}

@app.get("/api/servers")
async def list_servers(request: Request):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    servers = get_user_servers(user_id)
    return {"servers": [dict(s) for s in servers]}

@app.get("/api/ping/{server_id}")
async def ping_server_route(request: Request, server_id: int):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    server = query_db("SELECT * FROM servers WHERE id = ? AND user_id = ?", (server_id, user_id), one=True)
    if not server:
        return {"connected": False, "ping": "err"}
    
    return await ping_server(server["ip"], server["port"])

@app.get("/api/stats")
async def stats(request: Request):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    active_server = get_active_server(user_id)
    if not active_server:
        return {"stacks": [], "containers": [], "counts": {}, "ping": "--", "connected": False, "error": "No server selected"}
    
    return await get_docker_stats(active_server["ip"], active_server["port"])

@app.post("/api/container/{container_id}/{action}")
async def container_action_route(request: Request, container_id: str, action: str):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    active_server = get_active_server(user_id)
    if not active_server:
        return JSONResponse(status_code=400, content={"status": "error", "message": "No server selected"})
    
    return await container_action(active_server["ip"], active_server["port"], container_id, action)

@app.post("/api/stack/{stack_name}/{action}")
async def stack_action_route(request: Request, stack_name: str, action: str):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    active_server = get_active_server(user_id)
    if not active_server:
        return JSONResponse(status_code=400, content={"status": "error", "message": "No server selected"})
    
    return await stack_action(active_server["ip"], active_server["port"], stack_name, action)

@app.get("/api/server/{server_id}/stats")
async def server_stats(request: Request, server_id: int):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    server = query_db("SELECT * FROM servers WHERE id = ? AND user_id = ?", (server_id, user_id), one=True)
    if not server:
        return {"connected": False, "error": "Server not found"}
    
    return await get_docker_stats(server["ip"], server["port"])

@app.post("/api/server/{server_id}/stack/{stack_name}/{action}")
async def server_stack_action(request: Request, server_id: int, stack_name: str, action: str):
    user_id = get_current_user(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Not logged in"})
    
    server = query_db("SELECT * FROM servers WHERE id = ? AND user_id = ?", (server_id, user_id), one=True)
    if not server:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Server not found"})
    
    return await stack_action(server["ip"], server["port"], stack_name, action)

@app.get('/favicon.ico')
async def favicon():
    return FileResponse("static/img/logo.svg")
