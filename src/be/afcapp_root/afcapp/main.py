import os
from asyncio import sleep

from afcapp.db.church_db import ChurchDb
from afcapp.environment.env_wrapper import EnvReader
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

env_reader = EnvReader()
conn_str = env_reader.conn_str
db = ChurchDb(conn_str)

try:
    print('----trying to connect to db')
    db.test_connect()
except Exception as err:
    print(err)
    

# print(conn_str)

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

@app.get('/healthcheck')
async def healthcheck():
    return {"status": "ok"}

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
    await sleep(0.5)
    return fake_db[movie_id]