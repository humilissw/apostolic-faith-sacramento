from fastapi import FastAPI
from fastapi.testclient import TestClient
from afcapp.main import app

client = TestClient(app)