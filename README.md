# simple-otel-logger-py

## installation 

if using **uv** \
``` bash
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
    "hostname": "devang-kamdar",
    "timestamp": "2026-06-02T09:42:36.404950Z",
    "level": "info"
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

##  Example Output

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
    "hostname": "devang-kamdar",
    "timestamp": "2026-06-02T11:27:21.240551Z",
    "level": "info"
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
    "hostname": "devang-kamdar",
    "timestamp": "2026-06-02T11:27:21.241487Z",
    "level": "info"
}
```
## Features 
### This provides observability for 
- Microservices and Production grade debugging