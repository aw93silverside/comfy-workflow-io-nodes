"""API output nodes.

Output nodes mark which results the runner returns to callers AND control the
client-facing filename. The filename is authored IN THE GRAPH: wire the
``filename`` input from anything (an intermediate caption, a seed, a
concatenation node) for fully dynamic names, or fall back to the
``filename_template`` widget for static names. The node saves the file under
the resolved name, and the runner returns exactly that name (the parser emits
these nodes as an allowlist, so no server-side renaming happens).

All output nodes are OUTPUT_NODE and also pass their media straight through, so
they can sit mid-graph without dead-ending a branch.
"""

import os
import re

from .common import CATEGORY_OUTPUT


_SAFE_NAME = re.compile(r"[^A-Za-z0-9._\- ]+")


def _resolve_basename(filename: str, filename_template: str, output_name: str) -> str:
    """Pick the filename source (wired > template > output_name), strip any
    extension the user included, and sanitize to a filesystem-safe stem."""
    raw = (filename or "").strip() or (filename_template or "").strip() or (output_name or "").strip() or "output"
    raw = os.path.splitext(raw)[0]
    safe = _SAFE_NAME.sub("_", raw).strip() or "output"
    return safe


def _output_path(directory: str, basename: str, ext: str) -> tuple[str, str]:
    """Return (filename, fullpath) for an output.

    The client-facing filename must be STABLE across runs, so we deliberately do
    NOT dedup against the (persistent) workspace output directory — doing so made
    a requested ``result.png`` drift to ``result_2.png`` on every repeat call.
    The runner assigns each returned file a unique R2 key regardless, so
    overwriting a stale local file of the same name is harmless. Multiple images
    from a single node are disambiguated by the caller via the batch index.
    """
    filename = f"{basename}.{ext}"
    return filename, os.path.join(directory, filename)


class WorkflowIOImageOutput:
    """Return an image (or image batch) to the caller with a controlled filename."""

    CATEGORY = CATEGORY_OUTPUT
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "output_name": ("STRING", {
                    "default": "image",
                    "tooltip": "API output name/key. Also the fallback filename if no template/wire is set.",
                }),
                "filename_template": ("STRING", {
                    "default": "",
                    "tooltip": "Static filename (no extension). Overridden by the wired 'filename' input if connected.",
                }),
                "format": (["png", "jpg", "webp"], {"default": "png"}),
                "include": ("BOOLEAN", {"default": True,
                                        "tooltip": "If false, this output is produced in-graph but NOT returned to the caller."}),
            },
            "optional": {
                "filename": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Dynamic filename (no extension) wired from anywhere in the graph. Takes priority.",
                }),
            },
        }

    def run(self, images, output_name, filename_template, format, include, filename=""):
        if not include:
            return {"ui": {"images": []}, "result": (images,)}

        import numpy as np
        from PIL import Image
        import folder_paths

        out_dir = folder_paths.get_output_directory()
        basename = _resolve_basename(filename, filename_template, output_name)
        ext = format.lower()
        results = []

        batch = images.shape[0] if hasattr(images, "shape") else len(images)
        for i in range(batch):
            arr = 255.0 * images[i].cpu().numpy()
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            stem = basename if batch == 1 else f"{basename}_{i + 1}"
            fname, fpath = _output_path(out_dir, stem, ext)
            if ext in ("jpg", "jpeg"):
                img.convert("RGB").save(fpath, quality=95)
            elif ext == "webp":
                img.save(fpath, quality=95)
            else:
                img.save(fpath, compress_level=4)
            results.append({"filename": fname, "subfolder": "", "type": "output"})

        return {"ui": {"images": results}, "result": (images,)}


class WorkflowIOVideoOutput:
    """Save a VIDEO (from WorkflowIOVideoInput, CreateVideo, LoadVideo, VHS
    nodes, or anything else that produces the native VIDEO type) with a
    controlled filename and return it. Delegates to ``comfy_api``'s
    ``VideoInput.save_to`` (same mechanism as ComfyUI core's SaveVideo), which
    carries the audio track through — this is why the node takes a VIDEO
    rather than a bare IMAGE frame batch: frames alone have no audio to
    preserve. Passes the video through so it can sit mid-graph.
    """

    CATEGORY = CATEGORY_OUTPUT
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)

    @classmethod
    def INPUT_TYPES(cls):
        from comfy_api.util import VideoContainer

        return {
            "required": {
                "video": ("VIDEO",),
                "output_name": ("STRING", {"default": "video"}),
                "filename_template": ("STRING", {"default": "", "tooltip": "Static filename (no extension)."}),
                "format": (VideoContainer.as_input(), {
                    "default": "auto",
                    "tooltip": "'auto' remuxes the video's original container/codec (fast, lossless, audio intact). "
                                "Other options force re-encoding to that container.",
                }),
                "include": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "filename": ("STRING", {"forceInput": True, "tooltip": "Dynamic filename (no extension). Takes priority."}),
            },
        }

    def run(self, video, output_name, filename_template, format, include, filename=""):
        if not include:
            return {"ui": {"videos": []}, "result": (video,)}

        from comfy_api.util import VideoContainer
        import folder_paths

        out_dir = folder_paths.get_output_directory()
        container = VideoContainer(format)
        ext = VideoContainer.get_extension(container) or "mp4"
        basename = _resolve_basename(filename, filename_template, output_name)
        fname, fpath = _output_path(out_dir, basename, ext)

        video.save_to(fpath, format=container)

        return {
            "ui": {"videos": [{"filename": fname, "subfolder": "", "type": "output"}]},
            "result": (video,),
        }
