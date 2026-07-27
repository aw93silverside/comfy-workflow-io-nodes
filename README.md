# swordfish-comfy-nodes

Custom ComfyUI nodes that let a workflow author declare its **Swordfish API
contract inside the graph** — inputs and outputs — instead of hand-mapping them
in the Swordfish deploy UI. When the workflow is exported as API JSON, these
nodes carry all the contract metadata as widget values, and Swordfish's parser
reads them to auto-build the entire `api_config`.

## The idea

- **Input nodes** are passthrough: they hold a `value` and output it, so you
  wire their output into whatever downstream node needs it. Swordfish overrides
  `value` per API call. The injection target is always the Swordfish node's own
  `value` field — stable and unambiguous, so it never points into a third-party
  node the user might swap out.
- **Output nodes** mark what gets returned to the caller and control the
  client-facing filename — authored in the graph (wire the `filename` input for
  fully dynamic names, e.g. from an intermediate caption or seed).

## Nodes

### Inputs (`Swordfish/Inputs`)
| Node | Output | Notes |
|------|--------|-------|
| Swordfish Text Input | STRING | single/multi-line |
| Swordfish Int Input | INT | min/max/step |
| Swordfish Float Input | FLOAT | min/max/step |
| Swordfish Bool Input | BOOLEAN | |
| Swordfish Enum Input | STRING | `options` (one per line) → API enum allowlist |
| Swordfish Seed Input | INT | `randomize_if_omitted` |
| Swordfish Image Input | IMAGE, MASK | LoadImage-style; reads the file Swordfish writes to the input dir |
| Swordfish Video Input | VIDEO | LoadVideo-style; reads the file Swordfish writes to the input dir, decoding deferred to whatever consumes the VIDEO |

Every input node shares this metadata block: `param_name` (the API key),
`required`, `description`, `example`, `advanced`, `group`, `order`.

### Outputs (`Swordfish/Outputs`)
| Node | Takes | Notes |
|------|-------|-------|
| Swordfish Image Output | IMAGE | full saver (png/jpg/webp); passthrough IMAGE |
| Swordfish Video Output | IMAGE frames | encodes via imageio-ffmpeg (mp4/webm); passthrough IMAGE (audio muxing not yet) |

Output nodes are `OUTPUT_NODE` and pass their media through, so they can sit
mid-graph without dead-ending a branch.

> **MVP scope note:** Image and video input/output are fully implemented.
> Video input returns a native VIDEO handle (LoadVideo-style, audio preserved);
> video output still takes IMAGE frames and encodes via imageio-ffmpeg (audio
> muxing not yet). Text/Audio/File output nodes are planned fast-follows.

## Exported-JSON → api_config contract

Each Swordfish node serializes its widgets into the API JSON `inputs`. The
parser maps:

```
SwordfishTextInput node "2"  ->  api_config.mappings["prompt"] = {
    node_id: "2", field: "value", type: "string", required: true,
    default: {enabled: true, value: "a photograph of a cat"},
    tooltip: "<description>", advanced_setting: false }

SwordfishImageOutput node "8"  ->  api_config.output_nodes = ["8", ...]
```

Because `output_nodes` is emitted as an allowlist (not a rename map), the runner
returns each output with the exact filename the node saved — no server-side
renaming. See [`examples/sample_api_workflow.json`](examples/sample_api_workflow.json)
for the full exported shape the parser consumes.

## Install

The node folder just needs to live in a ComfyUI `custom_nodes/` directory.

- **Local / interactive dev:** clone into `ComfyUI/custom_nodes/` and restart.
- **Swordfish v3 runner** (`modal/v3/comfyui.py`): add this repo's URL to the
  `CUSTOM_NODES` list (cloned at image build).
- **Swordfish v2 editor + runner** (workspace-based): the folder must be present
  in each workspace's `custom_nodes/`. Because these are platform nodes that must
  exist everywhere, prefer baking them into the base image + a startup symlink
  into the active workspace rather than per-workspace installs. **Deploy to both
  the editor (`comfyui-instance-v2`) and the runner (`comfyui-api-runner-v2`)** —
  installing only one leaves the other failing at cold start.

No third-party pip dependencies (uses ComfyUI's existing torch/numpy/Pillow).

## Dev

```bash
# contract smoke test (no ComfyUI needed — heavy imports are lazy inside run())
python3 -c "from swordfish_nodes import NODE_CLASS_MAPPINGS; print(len(NODE_CLASS_MAPPINGS))"
```
