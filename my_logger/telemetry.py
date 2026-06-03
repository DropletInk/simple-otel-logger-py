from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


def setup_tracing():
    trace.set_tracer_provider(TracerProvider())


def create_span(name):
    tracer = trace.get_tracer("my_logger")

    return tracer.start_as_current_span(name)
