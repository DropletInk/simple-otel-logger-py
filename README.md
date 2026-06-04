# simple-otel-logger-py

## installation

if using **uv** \

```bash
uv add git+https://github.com/DropletInk/simple-otel-logger-py.git
```

## Requirements

```bash
Python 3.9+
opentelemetry-api
```

## Environment Configuration

```js
ENVIRONMENT = development (or deployment)
LOG_LEVEL = INFO (or DEBUG)
SERVICE_NAME = app-service ( or the name of the service being used )
```

## Basic Usage

```py
from my_logger import get_logger

logger = get_logger()

logger.info("Application started")
logger.warn("Cache miss")
logger.error("Login failed", {"user_id": 42})
logger.debug("Debug details", {"step": 2})

```

## For Tracing with the help of Open-Telemetry

Create app for FastApi then import

```py
from my_logger import get_logger
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
logger = get_logger()

app = FastAPI(title="Sample FastAPI Application", version="1.0.0")

FastAPIInstrumentor().instrument_app(app)
```

Output

```bash
{
    "service": "app-service",
    "event": "Random status generated: processing",
    "trace_id": "5e5eccf6ba765eddd0396349373f1b05",
    "span_id": "479a380d4523faad",
    "trace_flags": 3,
    "hostname": "devang-kamdar",
    "severityText": "INFO",
    "severityNumber": 9,
    "timestamp": "2026-06-02T09:42:36.404950Z"
}
```

## For Metrics Visualization

```py

from my_logger import get_logger,metrics_router
app.include_router(metrics_router, prefix="", tags=["Metrics"])

```

After Adding the above code will add a default endpoint for metrics

## For the middlewares

```py

app.middleware("http")(logging_middleware)

```

## Example Output

### Request

```bash
{
    "service": "app-service",
    "method": "GET",
    "path": "/health",
    "event": "request_started",
    "request_id": "8562d006-9c24-487a-9f0e-2279c2eaabf0",
    "trace_id": "e6a507d3ed0e3cedb09bb309f6516d35",
    "span_id": "4de66871bad4b4f3",
    "trace_flags": 3,
    "hostname": "devang-kamdar",
    "severityText": "INFO",
    "severityNumber": 9,
    "timestamp": "2026-06-02T11:27:21.240551Z"
}
```

### Reponse

```bash
{
    "service": "app-service",
    "status_code": 200,
    "duration": 0.0009,
    "event": "request_completed",
    "request_id": "8562d006-9c24-487a-9f0e-2279c2eaabf0",
    "trace_id": "e6a507d3ed0e3cedb09bb309f6516d35",
    "span_id": "4de66871bad4b4f3",
    "trace_flags": 3,
    "hostname": "devang-kamdar",
    "severityText": "INFO",
    "severityNumber": 9,
    "timestamp": "2026-06-02T11:27:21.241487Z"
}
```

## To Add Custom Spans

Code Example

```py
from my_logger import create_span

@app.get("/")
async def root():
    with create_span("root"):
        message = "Welcome to the Sample FastAPI Application with Structured Logging and OpenTelemetry!"
        logger.info("Root endpoint accessed", message=message)
    return {"message": "FastAPI Application Running"}
```

Result

```bash
{
    "service": "my-fastapi-service",
    "message": "Welcome to the Sample FastAPI Application with Structured Logging and OpenTelemetry!",
    "event": "Root endpoint accessed",
    "request_id": "98a9b541-7513-4126-84e1-37d764208ee0",
    "trace_id": "a2f415fc4b42b80af2dc54ab75f4621b",
    "span_id": "f6dba492f9c4cb5c",
    "trace_flags": 3,
    "hostname": "devang-kamdar",
    "severityText": "INFO",
    "severityNumber": 9,
    "timestamp": "2026-06-04T05:08:13.255731Z"
}
```

## Features

### This provides observability for

- Microservices and Production grade debugging
- Custom Spans can be added
