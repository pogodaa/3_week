# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models import User

from app.crud import users as crud_users
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "frontend" / "templates")

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def role_to_code(role: str) -> str:
    mapping = {
        "Менеджер": "manager",
        "Мастер": "specialist",
        "Оператор": "operator",
        "Заказчик": "client",
        "Админ": "admin"
    }
    return mapping.get(role, "guest")

def code_to_role_display(code: str) -> str:
    """Преобразует внутренний код роли в читаемое название для отображения."""
    mapping = {
        "manager": "Менеджер",
        "specialist": "Мастер",
        "operator": "Оператор",
        "client": "Заказчик",
        "admin": "Администратор"
    }
    return mapping.get(code, code)

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_login(db, login)
    if not user or not crud_users.verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"},
            status_code=401
        )
    
    response = RedirectResponse(url="/", status_code=303)
    role_code = role_to_code(user.type)
    response.set_cookie(key="user_role", value=role_code)
    # Не сохраняем кириллицу в cookie (HTTP cookie поддерживают только latin-1)
    # Преобразование будет делаться в get_user_role_display()
    response.set_cookie(key="user_id", value=str(user.userID))
    return response

@router.get("/logout", response_class=RedirectResponse)
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_role")
    response.delete_cookie("user_id")
    return response