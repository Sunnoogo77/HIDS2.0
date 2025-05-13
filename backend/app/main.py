from fastapi import FastAPI
from app.api import status

app = FastAPI(
    title="HIDS-Web API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.include_router(status.router)