from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

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

# Read input text from file
input_file_path = "90s_Founder_in_SF/txt/ch_1_90s_Founder_in_SF.txt"  # Replace with your text file path
input_path = Path(input_file_path)
base_name = input_path.stem  # Gets filename without extension

# Read the file
with open(input_file_path, 'r', encoding='utf-8') as file:
    input_text = file.read()

# Split text into chunks
text_chunks = chunk_text(input_text, MAX_CHARACTERS)

# Create audio files for each chunk and build JSON data
json_data = []
for i, chunk in enumerate(text_chunks):
    speech_file_path = Path(__file__).parent / f"{base_name}_{i+1}.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=chunk,
    )
    response.stream_to_file(speech_file_path)
    print(f"Created: {speech_file_path}")
    
    # Add entry to JSON data
    json_data.append({
        "audio_file": str(speech_file_path),
        "text": chunk
    })

# Write JSON data to file
json_file_path = Path(__file__).parent / f"{base_name}_audio_mapping.json"
with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2)
print(f"Created JSON mapping file: {json_file_path}")