from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from devpulse_server.database.connection import get_db
from devpulse_server.api.ingest.models.event_models import EventRequest
from typing import Annotated
from devpulse_server.database.tables.user import User
from devpulse_server.database.tables.device import Device
from devpulse_server.api.credentials.router import get_current_user_and_device
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from devpulse_server.database.tables.event import Event, EventType

router = APIRouter(prefix="/api/ingest", tags=["ingest"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/events")
async def ingest_events(
    events: EventRequest,
    user_device: Annotated[tuple[User, Device], Depends(get_current_user_and_device)],
    db: AsyncSession = Depends(get_db),
):
    if not events:
        return {"message": "No events to ingest"}

    user, device = user_device

    try:
        to_commit = []
        for event in events.events:
            if event.__class__.__name__ == "ActivityEvent":
                db_event = Event(
                    user_id=user.user_id,
                    device_id=device.device_id,
                    event_type=EventType.activity,
                    timestamp=event.timestamp,
                    event=event.event,
                    username=event.username,
                )
            elif event.__class__.__name__ == "HeartbeatEvent":
                db_event = Event(
                    user_id=user.user_id,
                    device_id=device.device_id,
                    event_type=EventType.heartbeat,
                    timestamp=event.timestamp,
                    username=event.username,
                )
            elif event.__class__.__name__ == "WindowEvent":
                db_event = Event(
                    user_id=user.user_id,
                    device_id=device.device_id,
                    event_type=EventType.window,
                    timestamp=event.timestamp,
                    window_title=event.window_title,
                    duration=event.duration,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    username=event.username,
                )
            else:
                continue
            to_commit.append(db_event)
        db.add_all(to_commit)
        await db.commit()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing events: {exc}",
        )
    return {"message": f"Ingested {len(events.events)} events"}
