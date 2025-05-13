import os
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app = FastAPI(title="Road Network Management API",
              description="REST API for managing road networks, uploading, updating and retrieving road networks",
              version="1.0.0", )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Homepage."""
    return templates.TemplateResponse("homepage.html", {"request": request})
