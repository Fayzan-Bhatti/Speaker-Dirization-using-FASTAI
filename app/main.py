import openai
import asyncio
import os
from fastapi import FastAPI, Header
# from apis.transcription import transcribe


from app.routers import transcription, translation, takeaways, root, speakers

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("GPT3_API_KEY")
use_auth_token = os.getenv("PYANOTATE_AUTH_TOKEN")

app = FastAPI( title="SuperKool", version="0.0.1" )
app.include_router(transcription.router)
app.include_router(translation.router)
app.include_router(takeaways.router)
app.include_router(speakers.router)
app.include_router(root.router)
