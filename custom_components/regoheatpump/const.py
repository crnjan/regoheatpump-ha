"""Constants for the Rego Heat Pump integration."""

from .rego600 import RegoType

DOMAIN = "regoheatpump"

CONF_REGO_TYPE = "rego_type"

REGO_TYPE_LABELS = {
    RegoType.REGO637.value: "Rego 637",
    RegoType.REGO636.value: "Rego 636",
}

DEFAULT_REGO_TYPE = RegoType.REGO637.value
