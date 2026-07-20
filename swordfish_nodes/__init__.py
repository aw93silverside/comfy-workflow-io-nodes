"""Swordfish node pack — aggregates the class + display-name mappings."""

from .inputs import (
    SwordfishTextInput,
    SwordfishIntInput,
    SwordfishFloatInput,
    SwordfishBoolInput,
    SwordfishEnumInput,
    SwordfishSeedInput,
    SwordfishImageInput,
    SwordfishVideoInput,
)
from .outputs import (
    SwordfishImageOutput,
    SwordfishVideoOutput,
)

NODE_CLASS_MAPPINGS = {
    # Inputs
    "SwordfishTextInput": SwordfishTextInput,
    "SwordfishIntInput": SwordfishIntInput,
    "SwordfishFloatInput": SwordfishFloatInput,
    "SwordfishBoolInput": SwordfishBoolInput,
    "SwordfishEnumInput": SwordfishEnumInput,
    "SwordfishSeedInput": SwordfishSeedInput,
    "SwordfishImageInput": SwordfishImageInput,
    "SwordfishVideoInput": SwordfishVideoInput,
    # Outputs
    "SwordfishImageOutput": SwordfishImageOutput,
    "SwordfishVideoOutput": SwordfishVideoOutput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SwordfishTextInput": "Swordfish Text Input",
    "SwordfishIntInput": "Swordfish Int Input",
    "SwordfishFloatInput": "Swordfish Float Input",
    "SwordfishBoolInput": "Swordfish Bool Input",
    "SwordfishEnumInput": "Swordfish Enum Input",
    "SwordfishSeedInput": "Swordfish Seed Input",
    "SwordfishImageInput": "Swordfish Image Input",
    "SwordfishVideoInput": "Swordfish Video Input",
    "SwordfishImageOutput": "Swordfish Image Output",
    "SwordfishVideoOutput": "Swordfish Video Output",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
