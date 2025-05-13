import os
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.core.database import engine
from app.db import models
from app.api.v1.endpoints.users import router as users_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


app = FastAPI(title="Road Network Management API",
              description="REST API for managing road networks, uploading, updating and retrieving road networks",
              version="1.0.0", )

app.include_router(users_router)

models.Base.metadata.create_all(engine)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Homepage."""
    return templates.TemplateResponse("homepage.html", {"request": request})
