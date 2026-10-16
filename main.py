@app.post("/extract")
def extract_video(data: dict):
    video_url = data.get("url")
    if not video_url:
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        ydl_opts = {
            'skip_download': True,
        }
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
