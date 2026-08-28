from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Chatbot backend is working!"}