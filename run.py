#!/usr/bin/env python3
"""
Application entry point
"""
import uvicorn
from src.main import app
from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug
    )
