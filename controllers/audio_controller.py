from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uuid
from openai import OpenAI
import os
from dotenv import load_dotenv

router = APIRouter()
templates = Jinja2Templates(directory="views")

# Initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

MAX_CHARACTERS = 4096

def chunk_text(text, max_chars):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_chars:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

@router.post("/generate-audio")
async def generate_audio(text: str = Form(...)):
    if not text:
        return {"error": "No text provided"}
    
    try:
        output_dir = Path("static/audio")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"speech_{uuid.uuid4()}.mp3"
        speech_file_path = output_dir / filename
        
        text_chunks = chunk_text(text, MAX_CHARACTERS)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text_chunks[0],
        )
        
        response.stream_to_file(speech_file_path)
        
        return {"audio_url": f"/static/audio/{filename}"}
    
    except Exception as e:
        return {"error": str(e)}