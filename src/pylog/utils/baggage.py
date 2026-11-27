import os
from collections.abc import Mapping

from opentelemetry import baggage


_baggage_fields: dict[str, str] = {}


def configure_baggage_fields(
    baggage_fields: Mapping[str, str],
) -> None:
    global _baggage_fields
    _baggage_fields = dict(baggage_fields)


def configure_baggage_fields_from_env() -> None:
    raw_fields = os.getenv("PYLOG_BAGGAGE_FIELDS", "")
    baggage_fields: dict[str, str] = {}

    for field in raw_fields.split(";"):
        field = field.strip()

        if field:
            baggage_key, separator, attribute_name = field.partition(":")

            if not separator or not baggage_key.strip() or not attribute_name.strip():
                raise ValueError(
                    f"Invalid PYLOG_BAGGAGE_FIELDS entry: {field}"
                )

            baggage_fields[baggage_key.strip()] = attribute_name.strip()

    configure_baggage_fields(baggage_fields)


def enrich_attributes_with_baggage(
    attributes: Mapping[str, object] | None = None,
) -> dict[str, object]:
    enriched_attributes = dict(attributes or {})

    for baggage_key, attribute_name in _baggage_fields.items():
        baggage_value = baggage.get_baggage(baggage_key)

        if baggage_value is not None:
            enriched_attributes.setdefault(attribute_name, baggage_value)

    return enriched_attributes