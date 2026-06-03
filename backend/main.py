from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
import io

from backend.storage import get_storage_client

app = FastAPI(title="Audio Memory Map API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = get_storage_client()

@app.get("/")
def home():
    return {"message": "Audio Memory Map API is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/memories")
async def create_memory(
    title: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    transcript: str = Form(""),
    audio: UploadFile = File(...)
):
    try:
        # 1. Read file bytes
        file_bytes = await audio.read()
        
        # 2. Save raw audio to storage
        audio_ref = storage.save_audio(file_bytes, audio.filename)
        
        # 3. Simulate generating embedding if none provided (mock 128 floats vector)
        mock_embedding = [0.0] * 128
        
        # 4. Save metadata
        memory = storage.save_memory(
            title=title,
            lat=lat,
            lon=lon,
            audio_ref=audio_ref,
            transcript=transcript,
            embedding=mock_embedding
        )
        return {"status": "success", "memory": memory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories")
def list_memories():
    try:
        memories = storage.list_memories()
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories/{memory_ref}/audio")
def get_memory_audio(memory_ref: str):
    try:
        audio_bytes = storage.get_audio_bytes(memory_ref)
        
        # Infer content type based on extension
        content_type = "audio/wav"
        if memory_ref.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif memory_ref.endswith(".ogg"):
            content_type = "audio/ogg"
            
        return Response(content=audio_bytes, media_type=content_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
