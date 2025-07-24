from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/api/ingest", tags=["ingest"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/queue")
def queue_ingest(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
    """Queue data for ingestion."""
    return {"message": "Data queued"}


# @router.post("/flush")
# def flush_ingest(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
#     """Flush the ingest queue."""
#     return {"message": "Ingest queue flushed"}
