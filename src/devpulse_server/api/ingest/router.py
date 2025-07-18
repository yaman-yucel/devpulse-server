from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/queue")
def queue_ingest(request: Request) -> dict:
    """Queue data for ingestion."""
    return {"message": "Data queued"}


@router.post("/flush")
def flush_ingest(request: Request) -> dict:
    """Flush the ingest queue."""
    return {"message": "Ingest queue flushed"}
