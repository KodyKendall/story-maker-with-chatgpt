from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

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

# Initialize client with API key from environment variables
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Sample input text (you can replace this with your own text)
input_text = """Today is a wonderful day to build something people love! 
Here is a much longer text that we want to process and convert to speech."""

# Split text into chunks
text_chunks = chunk_text(input_text, MAX_CHARACTERS)

# Create audio files for each chunk
for i, chunk in enumerate(text_chunks):
    speech_file_path = Path(__file__).parent / f"speech_{i+1}.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=chunk,
    )
    response.stream_to_file(speech_file_path)
    print(f"Created: {speech_file_path}")