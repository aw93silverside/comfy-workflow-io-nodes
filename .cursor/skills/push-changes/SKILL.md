---
name: push-changes
description: >-
  Branch, implement, validate, and open PRs for the comfy-workflow-io-nodes
  ComfyUI custom-node pack. Use when changing Workflow IO nodes, contract
  widgets, or README in this repository, or when the user asks how to contribute
  or ship changes here.
---

# Pushing changes — comfy-workflow-io-nodes

## Before you code

1. Read [docs/comfy-json-ui-contract.md](../../../docs/comfy-json-ui-contract.md) — Comfy JSON vs Brand Brain UI boundary.
2. `git fetch origin` and branch from **`origin/main`** (this repo has no `develop`).
3. Use a descriptive branch name (`feature/…`, `fix/…`, or `pedrosacramento/sil-####-…` when tied to Linear).

## Implementing contract changes

- Put shared widget vocab in `api_nodes/common.py` (`VALUE_TYPES`, `meta_widgets`, `value_type_widget`).
- New metadata fields: **`optional`** in `INPUT_TYPES` when possible; default so missing = old behavior.
- Register nodes in `api_nodes/__init__.py` (`NODE_CLASS_MAPPINGS`, display names).
- Update the **Nodes** table in root `README.md` for any new or changed public widgets.
- `run()` should stay passthrough unless the node loads media (image/video). Semantic fields (`value_type`, `separator`) are for export/parser, not Comfy execution.

### `VALUE_TYPES` (append-only)

`VALUE_TYPES` in `common.py` is **read-only except for new entries at the end**. Never remove, rename, or reorder — saved workflows break. Only **append** new meanings; fix bad semantics with a new type, not by editing an old one. Full rationale: contract doc § `value_type` vocabulary.

## Validate locally

```bash
python3 -c "from api_nodes import NODE_CLASS_MAPPINGS; print(len(NODE_CLASS_MAPPINGS))"
```

Optional ComfyUI: symlink repo into `ComfyUI/custom_nodes/`, restart, add a node from **Workflow IO**, export API JSON and confirm new widgets appear under `inputs`.

There is **no CI** — do not claim checks you did not run.

## Pull request

- Target **`main`**.
- Title: Linear code first when applicable, e.g. `SIL-1730: …` (ticket title), not `(SIL-1730)` at the end.
- Body: short problem/solution blurb, **Changes** bullets (UI-facing widget names in **bold**), **Validation** (what you actually ran—succinct, no local-only file paths).
- Note if downstream work is required (backend `extract_workflow_io_nodes`, frontend mapping/composer) in a short “Out of scope” line when relevant.
- Deploy reminder when node set changes: staging **editor and runner** together (README Install).

## Do not

- Add pip dependencies without strong justification (README: none today).
- Break saved graphs by moving required widgets or **changing `VALUE_TYPES`** (no deletes, renames, or reorder).
- Commit secrets or `.env` backups.
