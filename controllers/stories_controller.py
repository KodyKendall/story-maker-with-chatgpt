from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os
from datetime import date

router = APIRouter()
templates = Jinja2Templates(directory="views")

@router.get("/stories")
async def stories(request: Request):
    
    stories_data = []
    stories_dir = "stories"
    
    # Iterate through story folders
    for story_folder in os.listdir(stories_dir):
        folder_path = os.path.join(stories_dir, story_folder)
        if os.path.isdir(folder_path):
            # Look for txt files in the txt subfolder
            txt_folder = os.path.join(folder_path, "txt")
            if os.path.exists(txt_folder):
                # Get first text file in the txt folder
                txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]
                if txt_files:
                    with open(os.path.join(txt_folder, txt_files[0]), 'r') as f:
                        content = f.read()[:100]  # First 100 characters
                    
                    stories_data.append({
                        "title": story_folder,
                        "author": "Kody",
                        "date": date.today().strftime("%Y-%m-%d"),
                        "content": content,
                        "filepath": folder_path  # Store the story's root folder path
                    })

    return templates.TemplateResponse(
        "stories.html",
        {
            "request": request,
            "name": "User",
            "stories": stories_data
        }
    )