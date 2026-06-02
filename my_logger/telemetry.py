from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


def setup_tracing():
    trace.set_tracer_provider(TracerProvider())
