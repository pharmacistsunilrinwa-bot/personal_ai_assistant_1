from fastapi import FastAPI
from endpoints import chat
import uvicorn

app = FastAPI(title="Personal AI Assistant Backend")

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to Personal AI Assistant API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
