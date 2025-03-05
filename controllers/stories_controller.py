from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="views")

@router.get("/stories")
async def stories(request: Request):
    # Sample stories data
    stories_data = [
        {
            "title": "The Adventure Begins",
            "author": "John Doe",
            "date": "2024-03-20",
            "content": "This is the beginning of an amazing journey..."
        },
        {
            "title": "A New Discovery",
            "author": "Jane Smith",
            "date": "2024-03-19",
            "content": "Scientists have made a breakthrough in quantum computing..."
        }
    ]

    return templates.TemplateResponse(
        "stories.html",
        {
            "request": request,
            "name": "User",
            "stories": stories_data  # Add stories to the template context
        }
    )