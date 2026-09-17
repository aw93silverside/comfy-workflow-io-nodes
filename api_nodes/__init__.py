"""API node pack — aggregates the class + display-name mappings."""

from .inputs import (
    ApiTextInput,
    ApiIntInput,
    ApiFloatInput,
    ApiBoolInput,
    ApiEnumInput,
    ApiSeedInput,
    ApiImageInput,
    ApiVideoInput,
)
from .outputs import (
    ApiImageOutput,
    ApiVideoOutput,
)

NODE_CLASS_MAPPINGS = {
    # Inputs
    "ApiTextInput": ApiTextInput,
    "ApiIntInput": ApiIntInput,
    "ApiFloatInput": ApiFloatInput,
    "ApiBoolInput": ApiBoolInput,
    "ApiEnumInput": ApiEnumInput,
    "ApiSeedInput": ApiSeedInput,
    "ApiImageInput": ApiImageInput,
    "ApiVideoInput": ApiVideoInput,
    # Outputs
    "ApiImageOutput": ApiImageOutput,
    "ApiVideoOutput": ApiVideoOutput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ApiTextInput": "API Text Input",
    "ApiIntInput": "API Int Input",
    "ApiFloatInput": "API Float Input",
    "ApiBoolInput": "API Bool Input",
    "ApiEnumInput": "API Enum Input",
    "ApiSeedInput": "API Seed Input",
    "ApiImageInput": "API Image Input",
    "ApiVideoInput": "API Video Input",
    "ApiImageOutput": "API Image Output",
    "ApiVideoOutput": "API Video Output",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
