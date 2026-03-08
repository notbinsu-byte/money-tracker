import uvicorn
import os

if __name__ == "__main__":
    debug = os.getenv("DEBUG", "false").lower() == "true"
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=8000,
        reload=debug,
    )
