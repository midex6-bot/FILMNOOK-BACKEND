class VideoRequest(BaseModel):
    url: str

@app.post("/extract")
def extract_video(data: VideoRequest):
    if not data.url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        ydl_opts = {
            "skip_download": True,
            "format": "best",  # Tries to fetch a single playable format
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(data.url, download=False)

        return {
            "success": True,
            "title": meta.get("title"),
            "duration": meta.get("duration"),
            "stream_url": meta.get("url"),
            "thumbnail": meta.get("thumbnail"),
        }

    except Exception as e:
        raise HTTPException(status_code=50
