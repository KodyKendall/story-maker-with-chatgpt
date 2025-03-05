from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import os
import json
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

@router.get("/story")
async def story(request: Request, filepath: str):
    root_directory = os.path.dirname(os.path.dirname(__file__))  # Go up two levels to reach project root
    try:
        # Validate filepath exists
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Story not found")
            
        # Get images data
        images_json_path = os.path.join(filepath, "images", "metadata.json")
        with open(images_json_path, 'r') as f:
            images_data = json.load(f)
            
        # Get audio data
        audio_json_path = os.path.join(filepath, "audio", "metadata.json") 
        with open(audio_json_path, 'r') as f:
            audio_data = json.load(f)
            
        # Make paths relative to static directory
        for image in images_data:
            image["image_url"] = os.path.basename(image["image_url"])
            
        for audio in audio_data:
            audio["audio_file"] = os.path.basename(audio["audio_file"])

        return templates.TemplateResponse(
            "story.html",
            {
                "request": request,
                "images": images_data,
                "audio_paths": audio_data
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/images/{filename}")
async def serve_story_image(filename: str):
    # Build the path to the image
    # Note: You might want to make this more dynamic based on the current story
    image_path = os.path.join(filename)
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path)

@router.get("/audio/{filename}")
async def serve_story_audio(filename: str):
    # Build the path to the image
    # Note: You might want to make this more dynamic based on the current story
    breakpoint()
    audio_path = os.path.join(filename)
    
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path)