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
templates = Jinja2Templates(directory="templates")
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

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-audio")
async def generate_audio(text: str = Form(...)):
    if not text:
        return {"error": "No text provided"}
    
    try:
        # Create output directory if it doesn't exist
        output_dir = Path("static/audio")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        filename = f"speech_{uuid.uuid4()}.mp3"
        speech_file_path = output_dir / filename
        
        # Split text into chunks if necessary
        text_chunks = chunk_text(text, MAX_CHARACTERS)
        
        # For simplicity, we'll just use the first chunk
        # You might want to handle multiple chunks differently
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text_chunks[0],
        )
        
        response.stream_to_file(speech_file_path)
        
        return {"audio_url": f"/static/audio/{filename}"}
    
    except Exception as e:
        return {"error": str(e)}

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

@app.get("/letters", response_model=List[Letter])
async def get_all_letters():
    try:
        with open("data/letters.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Letters not found")