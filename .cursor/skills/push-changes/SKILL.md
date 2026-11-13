---
name: push-changes
description: >-
  Contributing to comfy-workflow-io-nodes. Use when editing Workflow IO nodes or
  api_nodes/common.py, especially VALUE_TYPES and value_type.
---

# push-changes

Read [docs/comfy-json-ui-contract.md](../../../docs/comfy-json-ui-contract.md) for full context.

## `VALUE_TYPES` is append-only

In `api_nodes/common.py`, **`VALUE_TYPES` may only grow**: add new meanings at the **end** of the tuple. Never remove, rename, or reorder. Saved workflows store the chosen `value_type`; invalid entries break loading in ComfyUI. If a meaning is wrong, add a **new** type—leave existing values forever.
