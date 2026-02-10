# simple-otel-logger-py

## Local Install

### From the package root folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Install From Path (in another project):
```bash
pip install -e /path/to/simple_otel_logger_py
```

## ⚙️ Requirements
```bash
Python 3.9+
opentelemetry-api
```

### Install dependency:
```bash
pip install opentelemetry-api
```

## Basic Usage
```bash
from simple_otel_logger import Logger

logger = Logger(service_name="auth-service")

logger.info("Application started")
logger.warn("Cache miss")
logger.error("Login failed", {"user_id": 42})
logger.debug("Debug details", {"step": 2})
```
