"""Workflow IO node pack — aggregates the class + display-name mappings."""

from .inputs import (
    WorkflowIOTextInput,
    WorkflowIOIntInput,
    WorkflowIOFloatInput,
    WorkflowIOBoolInput,
    WorkflowIOEnumInput,
    WorkflowIOSeedInput,
    WorkflowIOImageInput,
    WorkflowIOVideoInput,
)
from .outputs import (
    WorkflowIOImageOutput,
    WorkflowIOVideoOutput,
)

NODE_CLASS_MAPPINGS = {
    # Inputs
    "WorkflowIOTextInput": WorkflowIOTextInput,
    "WorkflowIOIntInput": WorkflowIOIntInput,
    "WorkflowIOFloatInput": WorkflowIOFloatInput,
    "WorkflowIOBoolInput": WorkflowIOBoolInput,
    "WorkflowIOEnumInput": WorkflowIOEnumInput,
    "WorkflowIOSeedInput": WorkflowIOSeedInput,
    "WorkflowIOImageInput": WorkflowIOImageInput,
    "WorkflowIOVideoInput": WorkflowIOVideoInput,
    # Outputs
    "WorkflowIOImageOutput": WorkflowIOImageOutput,
    "WorkflowIOVideoOutput": WorkflowIOVideoOutput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WorkflowIOTextInput": "Workflow IO Text Input",
    "WorkflowIOIntInput": "Workflow IO Int Input",
    "WorkflowIOFloatInput": "Workflow IO Float Input",
    "WorkflowIOBoolInput": "Workflow IO Bool Input",
    "WorkflowIOEnumInput": "Workflow IO Enum Input",
    "WorkflowIOSeedInput": "Workflow IO Seed Input",
    "WorkflowIOImageInput": "Workflow IO Image Input",
    "WorkflowIOVideoInput": "Workflow IO Video Input",
    "WorkflowIOImageOutput": "Workflow IO Image Output",
    "WorkflowIOVideoOutput": "Workflow IO Video Output",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
