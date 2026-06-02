from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request Latency", ["method", "endpoint"]
)

ERROR_COUNT = Counter("http_errors_total", "Total Errors", ["method", "endpoint"])

ACTIVE_REQUESTS = Gauge("active_requests", "Active Requests")

router = APIRouter()


@router.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type="text/plain")
