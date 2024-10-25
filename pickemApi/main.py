"""
Main file of project.
"""

# main.py
from fastapi import FastAPI
from pickemApi.database import lifespan

from pickemApi.routers.user import router as user_router
from pickemApi.routers.tournaments import router as tournament_router
from pickemApi.routers.teams import router as team_router


app = FastAPI(lifespan=lifespan)


app.include_router(user_router, prefix="")
app.include_router(tournament_router, prefix="", tags=["tournament"])
app.include_router(team_router, prefix="", tags=["teams"])
