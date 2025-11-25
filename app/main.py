from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1 import sessions


def create_app() -> FastAPI:
    app = FastAPI(title="Pomodoro Timer API")
    app.include_router(sessions.router, prefix="/api/v1")
    # serve static frontend files (index.html) from /frontend
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
    return app


app = create_app()
