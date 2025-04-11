from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

monitoring_router = APIRouter()


@monitoring_router.get("/metrics")
def monitoring():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
