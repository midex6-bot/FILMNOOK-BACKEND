import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SUPABASE & TMDB CONFIGURATION ---
SUPABASE_URL = "https://giuljgypjtppmntyfcms.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpdWxqZ3lwanRwcG1udHlmY21zIiwicm9sZSI6"
    "ImFub24iLCJpYXQiOjE3OTIxNDQ4NTcsImV4cCI6MjEwNzcyMDg1N30."
    "rgyFrIsST-FYFciVX3sUwqM4vz50Pf7PIhtq7r97VU0"
)
TMDB_API_KEY = "4339b7f88c39cddd3d923ad8822e9ea5"


def get_tmdb_data(title):
  if not TMDB_API_KEY:
    return {}
  try:
    clean_title = title.split("-")[0].split("|")[0].strip()
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(clean_title)}"
    res = requests.get(search_url).json()
    if res.get("results"):
      movie = res["results"][0]
      return {
          "poster_url": (
              f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}"
              if movie.get("poster_path")
              else None
          ),
          "backdrop_url": (
              f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}"
              if movie.get("backdrop_path")
              else None
          ),
          "description": movie.get("overview"),
          "release_date": movie.get("release_date"),
      }
  except Exception:
    pass
  return {}


@app.post("/smart-ingest")
@app.post("/extract")
def smart_ingest(data: dict):
  single_url = data.get("url")
  urls = data.get("urls", [])
  queued_items = data.get("items", [])

  targets = []
  if single_url:
    targets.append(single_url)
  if urls:
    if isinstance(urls, str):
      targets.append(urls)
    elif isinstance(urls, list):
      targets.extend(urls)

  for item in queued_items:
    if item.get("url"):
      targets.append(item.get("url"))

  if not targets:
    raise HTTPException(status_code=400, detail="No valid URLs provided")

  results = []

  for target_url in targets:
    try:
      # 1. Get clean title via YouTube oEmbed (Never blocked on cloud servers)
      oembed_url = (
          f"https://www.youtube.com/oembed?url={target_url}&format=json"
      )
      oembed_res = requests.get(oembed_url, timeout=5)

      if oembed_res.status_code == 200:
        oembed_data = oembed_res.json()
        title = oembed_data.get("title", "FilmNook Feature Film")
      else:
        title = "FilmNook Feature Film"

      stream_url = target_url

      # 2. Fetch matching poster and description from TMDB
      tmdb_data = get_tmdb_data(title)

      # 3. Push directly into your Supabase database table using correct Python f-string
      payload = {
          "title": title,
          "duration": 120,
          "stream_url": stream_url,
          "poster_url": tmdb_data.get("poster_url"),
          "backdrop_url": tmdb_data.get("backdrop_url"),
          "description": tmdb_data.get("description"),
          "release_date": tmdb_data.get("release_date"),
      }

      headers = {
          "apikey": SUPABASE_KEY,
          "Authorization": f"Bearer {SUPABASE_KEY}",
          "Content-Type": "application/json",
          "Prefer": "return=minimal",
      }

      db_res = requests.post(
          f"{SUPABASE_URL}/rest/v1/movies", json=payload, headers=headers
      )

      if db_res.status_code in [200, 201]:
        results.append(
            {"title": title, "status": "success", "stream_url": stream_url}
        )
      else:
        results.append(
            {"target": target_url, "status": "db_error", "detail": db_res.text}
        )

    except Exception as e:
      results.append({"target": target_url, "status": "failed", "error": str(e)})

  return {"success": True, "processed": results}
