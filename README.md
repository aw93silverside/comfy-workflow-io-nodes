# comfy-workflow-io-nodes

Custom ComfyUI nodes that let a workflow author declare its **API contract
inside the graph** — inputs and outputs — instead of hand-mapping them in a
deploy UI. When the workflow is exported as API JSON, these nodes carry all
the contract metadata as widget values, and a workflow parser reads them to
auto-build the entire `api_config`.

## The idea

- **Input nodes** are passthrough: they hold a `value` and output it, so you
  wire their output into whatever downstream node needs it. The API runner
  overrides `value` per call. The injection target is always this node's own
  `value` field — stable and unambiguous, so it never points into a third-party
  node the user might swap out.
- **Output nodes** mark what gets returned to the caller and control the
  client-facing filename — authored in the graph (wire the `filename` input for
  fully dynamic names, e.g. from an intermediate caption or seed).

## Nodes

### Inputs (`Workflow IO/Inputs`)
| Node | Output | Notes |
|------|--------|-------|
| Workflow IO Text Input | STRING | single/multi-line |
| Workflow IO Int Input | INT | min/max/step |
| Workflow IO Float Input | FLOAT | min/max/step |
| Workflow IO Bool Input | BOOLEAN | |
| Workflow IO Enum Input | STRING | `options` (one per line) → API enum allowlist; optional `value_type` (`none`, `aspect_ratio`) says what each option means |
| Workflow IO Seed Input | INT | `randomize_if_omitted` |
| Workflow IO Image Input | IMAGE, MASK | LoadImage-style; reads the file the runner writes to the input dir |
| Workflow IO Video Input | VIDEO | LoadVideo-style; reads the file the runner writes to the input dir, decoding deferred to whatever consumes the VIDEO |

Every input node shares this metadata block: `param_name` (the API key),
`required`, `description`, `example`, `advanced`, `group`, `order`.

### Outputs (`Workflow IO/Outputs`)
| Node | Takes | Notes |
|------|-------|-------|
| Workflow IO Image Output | IMAGE | full saver (png/jpg/webp); passthrough IMAGE |
| Workflow IO Video Output | VIDEO | saves via `comfy_api`'s `VideoInput.save_to` (SaveVideo-style, audio preserved); passthrough VIDEO; `codec` (auto/h264/av1/prores, ComfyUI 0.44+) and a wirable `video_format` string (MP4, ProRes, WebM, MKV, auto) that overrides format + codec — ProRes is written as MOV (422 HQ, or 4444 for 4:4:4/alpha sources) |
| Workflow IO 3D Output | FILE_3D (GLB, glTF, FBX, OBJ, STL) | saves in the file's own format via `File3D.save_to` (Save 3D-style), reported under the `3d` UI key; passthrough FILE_3D |

Output nodes are `OUTPUT_NODE` and pass their media through, so they can sit
mid-graph without dead-ending a branch.

> **MVP scope note:** Image and video input/output are fully implemented, both
> preserving audio end-to-end via the native VIDEO type. Text/Audio/File
> output nodes are planned fast-follows.

## Exported-JSON → api_config contract

Each API node serializes its widgets into the API JSON `inputs`. The
parser maps:

```
WorkflowIOTextInput node "2"  ->  api_config.mappings["prompt"] = {
    node_id: "2", field: "value", type: "string", required: true,
    default: {enabled: true, value: "a photograph of a cat"},
    tooltip: "<description>", advanced_setting: false }

WorkflowIOImageOutput node "8"  ->  api_config.output_nodes = ["8", ...]
```

Because `output_nodes` is emitted as an allowlist (not a rename map), the runner
returns each output with the exact filename the node saved — no server-side
renaming. See [`examples/sample_api_workflow.json`](examples/sample_api_workflow.json)
for the full exported shape the parser consumes.

## Install

The node folder just needs to live in a ComfyUI `custom_nodes/` directory.

- **Local / interactive dev:** clone into `ComfyUI/custom_nodes/` and restart.
- **v3 runner** (`modal/v3/comfyui.py`): add this repo's URL to the
  `CUSTOM_NODES` list (cloned at image build).
- **v2 editor + runner** (workspace-based): the folder must be present
  in each workspace's `custom_nodes/`. Because these are platform nodes that must
  exist everywhere, prefer baking them into the base image + a startup symlink
  into the active workspace rather than per-workspace installs. **Deploy to both
  the editor (`comfyui-instance-v2`) and the runner (`comfyui-api-runner-v2`)** —
  installing only one leaves the other failing at cold start.

No third-party pip dependencies (uses ComfyUI's existing torch/numpy/Pillow).

## Dev

```bash
# contract smoke test (no ComfyUI needed — heavy imports are lazy inside run())
python3 -c "from api_nodes import NODE_CLASS_MAPPINGS; print(len(NODE_CLASS_MAPPINGS))"
```
