# simple-otel-logger-py

## installation

if using **uv** 

```bash
uv add git+https://github.com/DropletInk/simple-otel-logger-py.git --branch 3-adding-the-logging-library
```

## Environment Configuration

```js
Create a .env file :

ENVIRONMENT = development (or production)

// for traces export 
OTEL_EXPORTER_TRACE_ENDPOINT = http://localhost:4318/v1/traces

// for logs export
OTEL_EXPORTER_LOG_ENDPOINT = http://localhost:4318/v1/metrics

// for metrics export
OTEL_EXPORTER_METRICS_ENDPOINT = http://localhost:4318/v1/logs

```

## Basic Usage

```py
from pylog.logger import ConsoleLogger

log = ConsoleLogger("test-logger")

log.info("Your message here ......")

log.error("Your error message here ........")

log.warning("Your warning message here ..........")

log.debug("Your debug message here ..............")
```

## For Tracing with the help of Open-Telemetry

Create app for FastApi then import

```py
from pylog.logger import ConsoleLogger,traced
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
logger = ConsoleLogger()

app = FastAPI()
FastAPIInstrumentor().instrument_app(app)

@app.get("/health")
async def health_check():
    log.info("I am Inside the health check ")
    helper_function()
    return {"status": "healthy"}

@traced()
def helper_function()
    log.info("I am Inside the helper function ")
    return
```

Example Output

```bash
{
    "resources": {
        "service_name": "test-logger"
    },
    "instrumentationScope": {
        "name": "simple-otel-logger",
        "version": "1.0.0"
    },
    "timestamp": "2026-06-17 13:49:16",
    "severityText": "INFO",
    "severityNumber": 9,
    "event": "I am Inside the health check",
    "request_id": null,
    "span": {
        "trace_id": "e5df4e47a31162ab3fecb7abc03f7bc9",
        "span_id": "8823e7269477df95",
        "trace_flags": 3
    },
    "attributes": {}
}
{
    "resources": {
        "service_name": "test-logger"
    },
    "instrumentationScope": {
        "name": "simple-otel-logger",
        "version": "1.0.0"
    },
    "timestamp": "2026-06-17 13:49:16",
    "severityText": "INFO",
    "severityNumber": 9,
    "event": "I am Inside the helper function",
    "request_id": null,
    "span": {
        "trace_id": "e5df4e47a31162ab3fecb7abc03f7bc9",
        "span_id": "7741f238b956ec92",
        "trace_flags": 3
    },
    "attributes": {}
}
```

## For the middlewares

```py

from pylog.middleware import create_log_middleware

middleware = create_log_middleware(
    log,
    request_data=lambda req: {
        "method": req.method,
        "path": req.url.path,
        "query_params": str(req.query_params),
        "client_ip": req.client.host if req.client else None,
        "url": str(req.url),
        "ip_address": req.client.host if req.client else None,
        "user_agent": req.headers.get("user-agent"),
    },
    response_data=lambda req, res: {
        "status_code": res.status_code,
        "url": str(req.url),
        "handler": req.scope.get("endpoint").__name__
        if req.scope.get("endpoint")
        else None,
    },
)

app.middleware("http")(middleware)

```

## Example Output

### Request

```bash
{
    "resources": {
        "service_name": "test-logger"
    },
    "instrumentationScope": {
        "name": "simple-otel-logger",
        "version": "1.0.0"
    },
    "timestamp": "2026-06-17 14:04:30",
    "severityText": "INFO",
    "severityNumber": 9,
    "event": "Request Started",
    "request_id": "UUID('88c05dd3-f62e-4394-9525-a6458f353a7d')",
    "span": {
        "trace_id": "9ccf0fb1c0603b4efa40b3ed708360fb",
        "span_id": "9c13b91073038e4c",
        "trace_flags": 3
    },
    "attributes": {
        "method": "GET",
        "path": "/health",
        "query_params": "",
        "client_ip": "127.0.0.1",
        "url": "http://127.0.0.1:8000/health",
        "ip_address": "127.0.0.1",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.124.0 Chrome/148.0.7778.97 Electron/42.2.0 Safari/537.36"
    }
}
```

### Reponse

```bash
{
    "resources": {
        "service_name": "test-logger"
    },
    "instrumentationScope": {
        "name": "simple-otel-logger",
        "version": "1.0.0"
    },
    "timestamp": "2026-06-17 14:04:30",
    "severityText": "INFO",
    "severityNumber": 9,
    "event": "Response Received",
    "request_id": "UUID('88c05dd3-f62e-4394-9525-a6458f353a7d')",
    "span": {
        "trace_id": "9ccf0fb1c0603b4efa40b3ed708360fb",
        "span_id": "9c13b91073038e4c",
        "trace_flags": 3
    },
    "attributes": {
        "status_code": 200,
        "url": "http://127.0.0.1:8000/health",
        "handler": "health_check"
    }
}
```
## Features

### This provides observability for

- Microservices and Production grade debugging
- Middleware handeling is done 
