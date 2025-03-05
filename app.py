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
    title="Harper Family History and TTS API",
    description="API serving historical narratives with text-to-speech capabilities",
    version="1.0.0"
)

# Set up templates and static files
templates = Jinja2Templates(directory="views")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import controllers
from controllers import (
    home_controller
)

# Include routers
app.include_router(home_controller.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Harper Family Historical Archive"}