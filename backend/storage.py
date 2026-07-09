import os
import json
import uuid
import shutil
from pathlib import Path
import numpy as np

# Load Env config if available
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "LOCAL").upper()

class BaseStorage:
    def save_audio(self, file_bytes: bytes, filename: str) -> str:
        """Saves raw audio and returns a path or URL reference."""
        raise NotImplementedError

    def save_memory(self, title: str, lat: float, lon: float, audio_ref: str, transcript: str = "", embedding: list = None) -> dict:
        """Saves memory metadata, transcript, and embeddings."""
        raise NotImplementedError

    def list_memories(self) -> list:
        """Retrieves list of all memories."""
        raise NotImplementedError

    def get_audio_bytes(self, audio_ref: str) -> bytes:
        """Retrieves audio raw bytes."""
        raise NotImplementedError


class LocalStorage(BaseStorage):
    def __init__(self):
        data_dir_name = os.getenv("LOCAL_DATA_DIR", "data")
        upload_dir_name = os.getenv("LOCAL_UPLOAD_DIR", "uploads")
        
        self.data_dir = BASE_DIR / data_dir_name
        self.upload_dir = BASE_DIR / upload_dir_name
        
        self.data_dir.mkdir(exist_ok=True)
        self.upload_dir.mkdir(exist_ok=True)
        
        self.db_path = self.data_dir / "memories.json"

    def _load_db(self) -> list:
        if not self.db_path.exists():
            return []
        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_db(self, data: list):
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

    def save_audio(self, file_bytes: bytes, filename: str) -> str:
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(filename)[1] or ".wav"
        dest_filename = f"{file_id}{ext}"
        dest_path = self.upload_dir / dest_filename
        
        with open(dest_path, "wb") as f:
            f.write(file_bytes)
            
        # Return filename relative to uploads dir or unique id
        return dest_filename

    def save_memory(self, title: str, lat: float, lon: float, audio_ref: str, transcript: str = "", embedding: list = None) -> dict:
        db = self._load_db()
        memory_id = str(uuid.uuid4())
        
        memory = {
            "id": memory_id,
            "title": title,
            "lat": lat,
            "lon": lon,
            "audio_ref": audio_ref,
            "transcript": transcript,
            "embedding": embedding or []
        }
        db.append(memory)
        self._save_db(db)
        return memory

    def list_memories(self) -> list:
        return self._load_db()

    def get_audio_bytes(self, audio_ref: str) -> bytes:
        file_path = self.upload_dir / audio_ref
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file {audio_ref} not found locally.")
        with open(file_path, "rb") as f:
            return f.read()


class CloudStorage(BaseStorage):
    """
    Simulated or production integration for AWS S3 (for audio storage) 
    and PostgreSQL (for metadata/embeddings). Falls back nicely with helpful warnings.
    """
    def __init__(self):
        # We will attempt to import psycopg2 and boto3 here.
        # If credentials aren't set, we log warnings or fallback to local files.
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.db_url = os.getenv("POSTGRES_URL")
        
        # Fallback to local storage internally if cloud configs aren't supplied
        self.fallback = LocalStorage()
        
        self.has_s3 = bool(self.s3_bucket and os.getenv("AWS_ACCESS_KEY_ID"))
        self.has_db = bool(self.db_url)

    def save_audio(self, file_bytes: bytes, filename: str) -> str:
        if not self.has_s3:
            print("Warning: AWS S3 configs missing, falling back to local file storage for audio.")
            return self.fallback.save_audio(file_bytes, filename)
        
        import boto3
        s3 = boto3.client('s3')
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(filename)[1] or ".wav"
        s3_key = f"audio/{file_id}{ext}"
        
        s3.put_object(Bucket=self.s3_bucket, Key=s3_key, Body=file_bytes)
        return f"s3://{self.s3_bucket}/{s3_key}"

    def save_memory(self, title: str, lat: float, lon: float, audio_ref: str, transcript: str = "", embedding: list = None) -> dict:
        if not self.has_db:
            print("Warning: PostgreSQL config missing, falling back to local JSON database.")
            return self.fallback.save_memory(title, lat, lon, audio_ref, transcript, embedding)
        
        from psycopg2.extras import RealDictCursor

        from backend.db.connection import get_db_connection

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        memory_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO memories (id, title, lat, lon, audio_ref, transcript, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, lat, lon, audio_ref, transcript, embedding;
        """, (memory_id, title, lat, lon, audio_ref, transcript, embedding or []))
        
        memory = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return dict(memory)

    def list_memories(self) -> list:
        if not self.has_db:
            return self.fallback.list_memories()
            
        from psycopg2.extras import RealDictCursor

        from backend.db.connection import get_db_connection

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cur.execute("SELECT id, title, lat, lon, audio_ref, transcript, embedding FROM memories;")
            memories = cur.fetchall()
            return [dict(m) for m in memories]
        except Exception:
            return []
        finally:
            cur.close()
            conn.close()

    def get_audio_bytes(self, audio_ref: str) -> bytes:
        if not audio_ref.startswith("s3://"):
            return self.fallback.get_audio_bytes(audio_ref)
            
        import boto3
        s3 = boto3.client('s3')
        # Parse s3://bucket/key
        parts = audio_ref.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1]
        
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()


# Factory pattern helper
def get_storage_client() -> BaseStorage:
    if STORAGE_TYPE == "CLOUD":
        return CloudStorage()
    return LocalStorage()
