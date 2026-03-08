import uvicorn
import os

if __name__ == "__main__":
    debug = os.getenv("DEBUG", "false").lower() == "true"
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=debug,
    )
