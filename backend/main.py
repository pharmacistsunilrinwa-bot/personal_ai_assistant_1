from fastapi import FastAPI
from endpoints import chat, google_api, tasks, google_workspace, data_analysis, sentiment, pattern_recognition, file_manager
import uvicorn

app = FastAPI(title="Personal AI Assistant Backend")

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(google_api.router, prefix="/api/v1/google", tags=["Google Services"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Task Management"])
app.include_router(google_workspace.router, prefix="/api/v1/google-workspace", tags=["Google Workspace"])
app.include_router(data_analysis.router, prefix="/api/v1/analysis", tags=["Data Analysis"])
app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["Sentiment Analysis"])
app.include_router(pattern_recognition.router, prefix="/api/v1/logic", tags=["Pattern Recognition & Logic"])
app.include_router(file_manager.router, prefix="/api/v1/files", tags=["Local File System Automation"])

@app.get("/")
async def root():
    return {"message": "Welcome to Personal AI Assistant API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
