import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

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
    
    current_dir = os.path.dirname(__file__)
    cookies_path = os.path.join(current_dir, "cookies.txt.txt")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'quiet': True,
        'no_warnings': True,
    }
    
    if os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(video_url, download=False)
            
            return {
                "success": True,
                "title": meta.get("title"),
                "duration": meta.get("duration"),
                "stream url": meta.get("url"),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")
