from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/generate-audio")
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
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text_chunks[0],
        )
        
        response.stream_to_file(speech_file_path)
        
        return {"audio_url": f"/static/audio/{filename}"}
    
    except Exception as e:
        return {"error": str(e)}
