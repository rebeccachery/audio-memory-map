import json
import uuid
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "memories.json"
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)


def load_memories():

    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_memories(memories):

    with open(DATA_FILE, "w") as f:
        json.dump(memories, f, indent=2)


def add_memory(title, lat, lon, audio_path):

    memories = load_memories()

    memory_id = str(uuid.uuid4())

    destination = UPLOAD_DIR / f"{memory_id}.wav"

    shutil.copy(audio_path, destination)

    memory = {
        "id": memory_id,
        "title": title,
        "lat": lat,
        "lon": lon,
        "audio_path": str(destination),
    }

    memories.append(memory)

    save_memories(memories)

    return memory