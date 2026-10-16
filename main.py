from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract")
def extract_video(data: dict):
    video_url = data.get("url")
    if not video_url:
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        command = ["python", "-m", "yt-dlp", "-j", video_url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        meta = json.loads(result.stdout)

        return {
            "success": True,
            "title": meta.get("title"),
            "duration": meta.get("duration"),
            "stream_url": meta.get("url"),
            "thumbnail": meta.get("thumbnail")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
