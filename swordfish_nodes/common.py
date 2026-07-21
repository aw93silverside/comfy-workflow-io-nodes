"""Shared constants and widget helpers for the Swordfish node pack.

Every Swordfish input node carries the same block of "API metadata" widgets.
Those widget values are what ComfyUI serializes into the exported API JSON, and
they are exactly what Swordfish's WorkflowParser reads to auto-build an
``api_config`` (no manual mapping). The runtime behaviour of the input nodes is
deliberately trivial: they pass ``value`` straight through. Swordfish overrides
``value`` per API call by injecting into this node's own ``value`` field.
"""

CATEGORY_INPUT = "Swordfish/Inputs"
CATEGORY_OUTPUT = "Swordfish/Outputs"


class _AnyType(str):
    """A type string that compares equal to every other type.

    ComfyUI validates links by comparing the source RETURN_TYPE against the
    target input type. COMBO inputs (e.g. KSampler.sampler_name / scheduler,
    CheckpointLoaderSimple.ckpt_name) have their option-list as their type, so a
    plain ``STRING`` output cannot connect to them. An output typed with this
    wildcard connects into any input, including combos. Standard ComfyUI idiom.
    """

    def __ne__(self, other):  # noqa: D105 - "not-equal" is always False
        return False


# Wildcard output type for nodes that feed COMBO/typed widgets (e.g. enums).
ANY_TYPE = _AnyType("*")

# Bumped when the widget contract changes so the parser can branch on it.
SWORDFISH_NODE_SCHEMA = "1"


def meta_widgets(default_required: bool = True) -> dict:
    """The metadata widgets shared by every input node.

    Returned as a plain dict so callers can splat it into INPUT_TYPES and add
    their type-specific ``value`` widget alongside.
    """
    return {
        "param_name": (
            "STRING",
            {
                "default": "",
                "tooltip": "API parameter name callers use in their request. Must be unique within the workflow.",
            },
        ),
        "required": (
            "BOOLEAN",
            {
                "default": default_required,
                "tooltip": "If true, callers must supply this input. If false, the current value is the default.",
            },
        ),
        "description": (
            "STRING",
            {
                "default": "",
                "multiline": True,
                "tooltip": "Human-readable description surfaced in the generated API docs.",
            },
        ),
        "example": (
            "STRING",
            {
                "default": "",
                "tooltip": "Example value shown in the API docs. Purely documentation.",
            },
        ),
        "advanced": (
            "BOOLEAN",
            {
                "default": False,
                "tooltip": "Mark as an advanced parameter (hidden behind a toggle in the caller UI).",
            },
        ),
        "group": (
            "STRING",
            {
                "default": "",
                "tooltip": "Optional group label for organizing related parameters in docs/UI.",
            },
        ),
        "order": (
            "INT",
            {
                "default": 0,
                "min": 0,
                "max": 9999,
                "tooltip": "Display order in the caller UI / docs (lower shows first).",
            },
        ),
    }


# The metadata widget names, in the order they appear. The parser can iterate
# these to strip metadata from a node's inputs and find the real payload field.
META_FIELDS = ("param_name", "required", "description", "example", "advanced", "group", "order")
