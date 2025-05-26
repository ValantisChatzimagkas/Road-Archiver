import os
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from app.api.v1.endpoints.authentication import router as authentication_router
from app.api.v1.endpoints.road_networks import router as road_networks_router
from app.api.v1.endpoints.users import router as users_router
from app.core.database import engine
from app.db import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app = FastAPI(
    title="Road Network Management API",
    description="REST API for managing road networks, uploading, updating and retrieving road networks",
    version="1.0.0",
    openapi_tags=[
        {"name": "users", "description": "Operations related to users"},
        {"name": "authentication", "description": "Login and security"},
        {"name": "Networks", "description": "Manage road network data"},
    ],
)

app.include_router(users_router)
app.include_router(authentication_router)
app.include_router(road_networks_router)

models.Base.metadata.create_all(engine)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """Homepage."""
    return templates.TemplateResponse("homepage.html", {"request": request})


@app.get("/health", tags=["Health"])
def health_check() -> Dict:
    return {"status": "ok"}
