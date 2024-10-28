"""
Main file of project.
"""

# main.py
from fastapi import FastAPI
from pickemApi.core.database import lifespan

from pickemApi.routers.user import router as user_router
from pickemApi.routers.tournaments import router as tournament_router
from pickemApi.routers.teams import router as team_router
from pickemApi.routers.events import router as event_router
from pickemApi.routers.user_answer import router as user_answer_router


app = FastAPI(lifespan=lifespan)


app.include_router(user_router, prefix="")
app.include_router(tournament_router, prefix="", tags=["tournament"])
app.include_router(team_router, prefix="", tags=["teams"])
app.include_router(event_router, prefix="", tags=["events"])
app.include_router(user_answer_router, prefix="", tags=["user_answers"])
