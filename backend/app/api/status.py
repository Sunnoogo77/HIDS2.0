from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["status"])

class StatusResponse(BaseModel):
    status: str
    file: str
    folder: str
    ip: str
    timestamp: datetime
    
@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Récupère le statut de l'application.
    """
    # Remplacez ces valeurs par la logique réelle pour obtenir le statut
    status = "OK"
    file = "example.txt"
    folder = "/path/to/folder"
    ip = "10.10.1.1"
    timestamp = datetime.now()
    return StatusResponse(
        status=status,
        file=file,
        folder=folder,
        ip=ip,
        timestamp=timestamp
    )