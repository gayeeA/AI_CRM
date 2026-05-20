from fastapi import FastAPI
from db import Base, engine
from schemas import InteractionCreate
from tools import log_interaction, fetch_interactions
from agent import app as agent_app

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/log")
def log(data: InteractionCreate):
    return log_interaction(data.dict())

@app.get("/interactions")
def get_all():
    return fetch_interactions()

@app.post("/chat")
def chat(message: dict):
    result = agent_app.invoke({"input": message["text"]})
    return result