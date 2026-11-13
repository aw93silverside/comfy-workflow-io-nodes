"""Shared constants and widget helpers for the API node pack.

Every API input node carries the same block of "API metadata" widgets.
Those widget values are what ComfyUI serializes into the exported API JSON, and
they are exactly what a workflow parser reads to auto-build an ``api_config``
(no manual mapping). The runtime behaviour of the input nodes is deliberately
trivial: they pass ``value`` straight through. The API runner overrides
``value`` per call by injecting into this node's own ``value`` field.
"""

CATEGORY_INPUT = "Workflow IO/Inputs"
CATEGORY_OUTPUT = "Workflow IO/Outputs"


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
NODE_SCHEMA = "1"

# What a value means, so the app can show it appropriately (aspect_ratio: ratios
# like 16:9, drawn as shapes). One vocabulary for every node that declares it.
# Only add to it: ComfyUI rejects a saved value that is no longer in the list.
VALUE_TYPES = ("none", "aspect_ratio")


def value_type_widget() -> dict:
    """The optional ``value_type`` widget, for a node's ``optional`` section.

    Optional so workflows saved before a node had it keep passing ComfyUI's
    validation; a missing value means ``none``.
    """
    return {
        "value_type": (
            list(VALUE_TYPES),
            {
                "default": "none",
                "tooltip": "What each value means, so the app can show it appropriately "
                "(aspect_ratio: ratios like 16:9, drawn as shapes).",
            },
        ),
    }


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
