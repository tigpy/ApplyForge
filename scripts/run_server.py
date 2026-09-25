"""
Server Runner Script for ApplyForge
"""
import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    from packages.shared.config import settings
    print(f"Starting {settings.APP_NAME} on http://localhost:8000 ...")
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=False)
