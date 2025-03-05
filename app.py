from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid
from pydantic import BaseModel
from typing import List, Optional
import json

load_dotenv()

app = FastAPI(
    title="Text to Speech Converter",
    description="Convert text to speech using OpenAI's TTS API",
    version="1.0.0"
)

# Set up templates and static files
templates = Jinja2Templates(directory="views")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

MAX_CHARACTERS = 4096  # TTS-1 has a limit of approximately 4096 characters

def chunk_text(text, max_chars):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        # +1 for the space between words
        if current_length + len(word) + 1 <= max_chars:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

# Import controllers (not views)
from controllers import home_controller, audio_controller

# Include routers
app.include_router(home_controller.router)
app.include_router(audio_controller.router)

app = FastAPI(
    title="Harper Family History API",
    description="An API serving the historical narrative of the Harper family during the American Revolution",
    version="1.0.0"
)

# Pydantic models
class Letter(BaseModel):
    date: str
    from_person: str
    to_person: str
    content: str

class HistoricalEvent(BaseModel):
    year: str
    title: str
    description: str
    letters: Optional[List[Letter]] = None

class HistoricalPeriod(BaseModel):
    period: str
    title: str
    events: List[HistoricalEvent]
    description: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Harper Family Historical Archive"}

@app.get("/periods", response_model=List[HistoricalPeriod])
async def get_historical_periods():
    try:
        with open("data/historical_periods.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Historical data not found")

@app.get("/periods/{period_id}", response_model=HistoricalPeriod)
async def get_period(period_id: str):
    try:
        with open("data/historical_periods.json", "r") as f:
            periods = json.load(f)
            for period in periods:
                if period["period"] == period_id:
                    return period
            raise HTTPException(status_code=404, detail="Period not found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Historical data not found")

@app.get("/chapter1")
async def chapter1(request: Request):
    # Keep the file paths as they are in your original HTML
    images = [
        {
            "chunkIndex": 1,
            "title": "San Francisco Contrasts",
            "description": "An expansive view of 1995 San Francisco's urban landscape...",
            "style": "Vivid, cinematic with a nostalgic tone",
            "image_url": "/90s_Founder_in_SF/images/raw_images/ch_1_1.jpg"
        },
        # ... rest of images ...
    ]
    
    audio_paths = [
        {
            "audio_file": "/90s_Founder_in_SF/audio/ch_1_90s_Founder_in_SF_1.mp3",
            "text": "Chapter 1: Silicon Dreams and Skyscrapers..."
        },
        # ... rest of audio paths ...
    ]
    
    return templates.TemplateResponse(
        "story_chapter_1.html",
        {
            "request": request,
            "images": images,
            "audio_paths": audio_paths
        }
    )