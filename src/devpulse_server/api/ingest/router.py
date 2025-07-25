from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from devpulse_server.database.connection import get_db
from devpulse_server.api.ingest.models.event_models import EventRequest
from typing import Annotated
from devpulse_server.database.tables.user import User
from devpulse_server.database.tables.device import Device
from devpulse_server.api.credentials.router import get_current_user_and_device
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from rich import print as rprint

router = APIRouter(prefix="/api/ingest", tags=["ingest"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/events")
async def ingest_events(
    events: EventRequest,
    user_device: Annotated[tuple[User, Device], Depends(get_current_user_and_device)],
    #db: Session = Depends(get_db),
):
    """
    Accepts a list of events in the request body and stores them.
    Returns 200 on success (your client clears the store on 200).
    """
    if not events:
        # still return 200 so the client can clear its queue if it sent an empty list
        return {"message": "No events to ingest"}

    user, device = user_device

    try:
        rprint(f"Received events for user: {user}, device: {device}")
        rprint(events.events)
    except Exception as exc:
        # You can log the exception here
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing events: {exc}",
        )

    
# @router.post("/flush")
# def flush_ingest(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
#     """Flush the ingest queue."""
#     return {"message": "Ingest queue flushed"}
