"""Constants for the Rego Heat Pump integration."""

from .rego600 import RegoType

DOMAIN = "regoheatpump"

CONF_REGO_TYPE = "rego_type"

REGO_TYPE_LABELS = {
    RegoType.REGO636: "Rego 636",
    RegoType.REGO637: "Rego 637",
}

DEFAULT_REGO_TYPE = RegoType.REGO637
