from fastapi import FastAPI

app = FastAPI()


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Road Network API is running"}
