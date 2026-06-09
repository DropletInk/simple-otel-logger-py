from .telemetry import get_meter

_metrics = {}


#  counter
def counter(name: str, description: str = "This ia a counter function", unit: str = "1"):
    meter = get_meter()

    if name not in _metrics:
        _metrics[name] = meter.create_counter(
            name=name,
            description=description,
            unit=unit,
        )

    return _metrics[name]


#  histogram
def histogram(name: str, description: str = "This is a histogram function", unit: str = "ms"):
    meter = get_meter()

    if name not in _metrics:
        _metrics[name] = meter.create_histogram(
            name=name,
            description=description,
            unit=unit,
        )

    return _metrics[name]


# custom metrics


def create_counter(name: str, description: str = "This is a counter function", unit: str = "1"):
    meter = get_meter()
    return meter.create_counter(
        name=name,
        description=description,
        unit=unit,
    )
