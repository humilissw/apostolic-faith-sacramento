from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
import logging
import time
from helpers import create_random_string

fake_db = {
    1: {"id": 1,
    "title": "Cinderella"
    },
    2: {"id": 2,
    "title": "Toy Story"
    }
}

file_path = "loremipsum.txt"

app = FastAPI()

# Hello World route
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Endpoint to retrieve a file
@app.get("/file/{file_name}")
async def get_file(file_name): 
    if os.path.exists(file_name): 
        return FileResponse(file_name)
    else:
        raise HTTPException(status_code=404, detail="File not found")


# Route for dynamic load testing
@app.get("/text/{text}")
async def read_text(text): 
    results = {'text': text}
    return results
    
# Route for theoretical database call
@app.get("/movies/{movie_id}")
async def get_movies(movie_id: int):
    time.sleep(0.5)
    return fake_db[movie_id]