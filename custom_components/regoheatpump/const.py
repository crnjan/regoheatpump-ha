"""Constants for the Rego Heat Pump integration."""

from .rego600 import REGO_TYPE_636, REGO_TYPE_637

DOMAIN = "regoheatpump"

CONF_REGO_TYPE = "rego_type"

REGO_TYPE_LABELS = {
    REGO_TYPE_636: "Rego 636",
    REGO_TYPE_637: "Rego 637",
}

DEFAULT_REGO_TYPE = REGO_TYPE_637
