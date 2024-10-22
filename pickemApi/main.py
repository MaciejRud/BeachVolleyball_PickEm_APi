"""
Main file of project.
"""

# main.py
from fastapi import FastAPI
from pickemApi.database import lifespan

from pickemApi.routers.user import router as user_router


app = FastAPI(lifespan=lifespan)


app.include_router(user_router, prefix="")
