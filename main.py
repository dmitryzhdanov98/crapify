# main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import requests
import random
import time

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def get_random_bad_movie():
    max_page = 20
    attempts = 5

    for i in range(attempts):
        page = random.randint(1, max_page)
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "sort_by": "vote_average.asc",
            "vote_average.lte": 4,
            "vote_count.gte": 10,
            "page": page
        }
        print(f"Попытка {i+1}: запрос страницы {page}")
        try:
            r = requests.get("https://api.themoviedb.org/3/discover/movie", params=params, timeout=5)
            r.raise_for_status()
            data = r.json().get("results", [])
            if data:
                movie = random.choice(data)
                print(f"Найден фильм: {movie['title']} (рейтинг {movie['vote_average']})")
                return movie
            else:
                print(f"Пустая страница {page}")
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
        time.sleep(1)

    return None

@app.get("/api/random-bad-movie")
def api_random_bad_movie():
    movie = get_random_bad_movie()
    if not movie:
        return {"error": "No movies found after multiple attempts"}

    return {
        "title": movie["title"],
        "rating": movie["vote_average"],
        "overview": movie["overview"],
        "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
        "release_date": movie.get("release_date", "N/A")
    }
