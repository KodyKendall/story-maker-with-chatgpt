from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="views")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",  # Rails-like template path
        {
            "request": request,
            "name": "User"
        }
    )