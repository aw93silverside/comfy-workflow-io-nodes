"""Swordfish Comfy Nodes — ComfyUI custom-node entrypoint.

ComfyUI loads this package from ``custom_nodes/`` and reads NODE_CLASS_MAPPINGS
and NODE_DISPLAY_NAME_MAPPINGS at boot.
"""

from .swordfish_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
