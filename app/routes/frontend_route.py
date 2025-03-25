from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

frontend_router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/templates")


@frontend_router.get("/login", response_class=HTMLResponse, name="login")
async def serve_login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@frontend_router.get("/account", response_class=HTMLResponse, name="account")
async def serve_account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})


@frontend_router.get("/", response_class=HTMLResponse, name="home")
async def serve_index(request: Request):
    return templates.TemplateResponse("auth/home.html", {"request": request})


# 🔥 Добавляем страницу со списком пользователей
@frontend_router.get("/users", response_class=HTMLResponse)
async def serve_users(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})


@frontend_router.get("/prompts", response_class=HTMLResponse)
async def serve_prompts(request: Request):
    return templates.TemplateResponse("prompt/manage_prompts.html", {"request": request})

# 🔥 Добавляем страницу детального просмотра пользователя


@frontend_router.get("/prompts/{prompt_id}", response_class=HTMLResponse)
async def serve_prompt_detail(request: Request, prompt_id: str):
    return templates.TemplateResponse("prompt/view_prompt.html", {"request": request, "prompt_id": prompt_id})
