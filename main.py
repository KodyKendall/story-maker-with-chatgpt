from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize client with API key from environment variables
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
    model="tts-1",
    voice="onyx",
    input="Today is a wonderful day to build something people love!",
)
response.stream_to_file(speech_file_path)

print(speech_file_path)