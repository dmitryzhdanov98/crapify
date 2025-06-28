from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import requests
import random

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/random-bad-movie")
def get_random_bad_movie():
    page = random.randint(1, 100)
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "vote_average.asc",
        "vote_average.lte": 4,
        "vote_count.gte": 50,
        "page": page
    }
    r = requests.get(url, params=params)
    data = r.json().get("results", [])
    if not data:
        return {"error": "No movies found"}

    movie = random.choice(data)
    return {
        "title": movie["title"],
        "rating": movie["vote_average"],
        "overview": movie["overview"],
        "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
        "release_date": movie["release_date"]
    }
