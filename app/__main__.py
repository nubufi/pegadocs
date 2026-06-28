import uvicorn

from app.main import create_application

if __name__ == "__main__":
    app = create_application()
    uvicorn.run(app, port=8000, log_config=None, log_level=None)
