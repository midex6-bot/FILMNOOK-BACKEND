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
    
    # Check what files are actually in the folder on Render
    current_dir = os.path.dirname(__file__)
    files_in_dir = os.listdir(current_dir)
    cookies_path = os.path.join(current_dir, "cookies.txt")
    
    print("Files currently on Render server:", files_in_dir)
    
    if not os.path.exists(cookies_path):
        raise HTTPException(
            status_code=500, 
            detail=f"cookies.txt is missing on the server! Files found: {files_in_dir}"
        )
    
    ydl_opts = {
        'format': 'best',
        'cookiefile': cookies_path
    }
    
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
