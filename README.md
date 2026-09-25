# simple-otel-logger-py

## installation

if using **uv**

```bash
uv add "git+ssh://git@github.com/DropletInk/simple-otel-logger-py.git
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

log.info("Your message here ......",eventName="Info Logging" )

log.error("Your error message here ........",eventName="Error Logging")

log.warning("Your warning message here ..........",eventName="Warning Logging")

log.debug("Your debug message here ..............",eventName="debug Logging")
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
    "span": {
        "trace_id": "e5df4e47a31162ab3fecb7abc03f7bc9",
        "span_id": "8823e7269477df95",
        "trace_flags": 3
    },
    "severityText": "INFO",
    "severityNumber": 9,
    "eventName": Null,
    "body": "I am Inside the health check",
    "attributes": {
    	"request_id": null,
    }
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
    "span": {
        "trace_id": "e5df4e47a31162ab3fecb7abc03f7bc9",
        "span_id": "8823e7269477df95",
        "trace_flags": 3
    },
    "severityText": "INFO",
    "severityNumber": 9,
    "eventName": Null,
    "body": "I am Inside the health check",
    "attributes": {
    	"request_id": null,
    }
}
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
    "span": {
        "trace_id": "9ccf0fb1c0603b4efa40b3ed708360fb",
        "span_id": "9c13b91073038e4c",
        "trace_flags": 3
    },
    "severityText": "INFO",
    "severityNumber": 9,
    "eventName":Null,
    "body": "Request Started",
    "attributes": {
        "method": "GET",
        "path": "/health",
        "query_params": "",
        "client_ip": "127.0.0.1",
        "url": "http://127.0.0.1:8000/health",
        "ip_address": "127.0.0.1",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.124.0 Chrome/148.0.7778.97 Electron/42.2.0 Safari/537.36",
        "request_id": "UUID('88c05dd3-f62e-4394-9525-a6458f353a7d')",
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
    "span": {
        "trace_id": "9ccf0fb1c0603b4efa40b3ed708360fb",
        "span_id": "9c13b91073038e4c",
        "trace_flags": 3
    },
    "severityText": "INFO",
    "severityNumber": 9,
    "event": "Response Received",
    "attributes": {
        "status_code": 200,
        "url": "http://127.0.0.1:8000/health",
        "handler": "health_check"
    	"request_id": "UUID('88c05dd3-f62e-4394-9525-a6458f353a7d')",
    }
}
```

## Features

### This provides observability for

- Microservices and Production grade debugging
- Middleware handeling is done




# Metrics

This library lets you track numbers about your app — like how many
requests you've handled, how long they took, or how much memory you're
using — and either print them to your console or send them to a
monitoring tool.

## Quick start

```python
from pylog.telemetry import add_metric_exporter, get_meter

#Turn metrics only once at the starting of the app 
add_metric_exporter()

#Get a meter — this is what you use to create trackers
meter = get_meter(__name__)

#Create a counter 
request_counter = meter.create_counter("app.requests")
request_counter.add(1, {"method": "GET", "path": "/api/users"})
```

By default, this prints a summary to your console every 5
seconds.

## Metrics prints 

**By default It prints on Console** — just prints to your terminal for development.

```python
add_metric_exporter()
```

**A real monitoring backend** — send metrics to something like Grafana or
an OpenTelemetry Collector by giving it a URL:

```python
add_metric_exporter(OTLP_Metric_exporter_endpoint="http://localhost:4318")
```

## The 3 types of trackers 

**Counter** — a number that only goes up. Use it for counting things.
```python
counter = meter.create_counter("app.requests")
counter.add(1)
```

**UpDownCounter** — a number that goes up and down. Use it for things
like "how many requests are happening right now."
```python
active = meter.create_up_down_counter("app.active_requests")
active.add(1)   
active.add(-1)  
```

**Histogram** — records a bunch of values so you can see the spread (not
just a total). Use it for things like request duration.
```python
duration = meter.create_histogram("app.request.duration")
duration.record(45.2)  # this request took 45.2 ms
```

**Gauge** — records the current value of something at this moment (not a
running total). Use it for things like current temperature or current
queue size.

```python
temp = meter.create_gauge("device.temperature")
temp.record(72.5)
```


## Adding extra detail with tags

You can attach a dictionary of tags to any measurement, so you can break
it down later (e.g. by method, status code, etc.):

```python
counter.add(1, {"method": "GET", "status_code": 200})
```

## Only show certain metrics on the console

If there's a lot of noise, tell it which metric names you actually care
about:

```python
add_metric_exporter(watched={"app.requests", "app.request.duration"})
```

## Automatic CPU/memory tracking

Want CPU and memory stats without writing any code for it?

```python
from pylog.telemetry import enable_system_metrics

enable_system_metrics()
```

Safe to call more than once — it only sets things up the first time.

## Flushing right away

Metrics normally get sent out every 5 seconds. If you want to send them
immediately (e.g. right before your app shuts down):

```python
from pylog.telemetry import force_flush_metrics

force_flush_metrics()
```

## Shutting down cleanly

If your app used metrics, shut it down properly before exiting — otherwise
a background thread stays alive and can cause errors:

```python
from pylog.telemetry import get_meter_provider

provider = get_meter_provider()
if provider is not None:
    provider.shutdown()
```
  