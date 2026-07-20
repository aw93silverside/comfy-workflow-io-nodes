"""Swordfish output nodes.

Output nodes mark which results Swordfish returns to callers AND control the
client-facing filename. The filename is authored IN THE GRAPH: wire the
``filename`` input from anything (an intermediate caption, a seed, a
concatenation node) for fully dynamic names, or fall back to the
``filename_template`` widget for static names. The node saves the file under
the resolved name, and Swordfish returns exactly that name (the parser emits
these nodes as an allowlist, so no server-side renaming happens).

All output nodes are OUTPUT_NODE and also pass their media straight through, so
they can sit mid-graph without dead-ending a branch.
"""

import os
import re
import shutil

from .common import CATEGORY_OUTPUT


_SAFE_NAME = re.compile(r"[^A-Za-z0-9._\- ]+")


def _resolve_basename(filename: str, filename_template: str, output_name: str) -> str:
    """Pick the filename source (wired > template > output_name), strip any
    extension the user included, and sanitize to a filesystem-safe stem."""
    raw = (filename or "").strip() or (filename_template or "").strip() or (output_name or "").strip() or "output"
    raw = os.path.splitext(raw)[0]
    safe = _SAFE_NAME.sub("_", raw).strip() or "output"
    return safe


def _unique_path(directory: str, basename: str, ext: str) -> tuple[str, str]:
    """Return (filename, fullpath) that does not collide in ``directory``."""
    filename = f"{basename}.{ext}"
    path = os.path.join(directory, filename)
    counter = 1
    while os.path.exists(path):
        filename = f"{basename}_{counter}.{ext}"
        path = os.path.join(directory, filename)
        counter += 1
    return filename, path


class SwordfishImageOutput:
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
            fname, fpath = _unique_path(out_dir, stem, ext)
            if ext in ("jpg", "jpeg"):
                img.convert("RGB").save(fpath, quality=95)
            elif ext == "webp":
                img.save(fpath, quality=95)
            else:
                img.save(fpath, compress_level=4)
            results.append({"filename": fname, "subfolder": "", "type": "output"})

        return {"ui": {"images": results}, "result": (images,)}


class SwordfishVideoOutput:
    """Return an already-produced video file to the caller with a controlled name.

    Takes ``video_path`` — the path/filename of a video produced upstream (e.g.
    the file written by VHS_VideoCombine) — copies it into the output directory
    under the resolved name, and registers it so Swordfish returns it.

    MVP note: this is a marker/rename node; it does not encode frames itself.
    """

    CATEGORY = CATEGORY_OUTPUT
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {
                    "default": "",
                    "tooltip": "Path or filename of the produced video (e.g. from VHS_VideoCombine).",
                }),
                "output_name": ("STRING", {"default": "video"}),
                "filename_template": ("STRING", {"default": "", "tooltip": "Static filename (no extension)."}),
                "include": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "filename": ("STRING", {"forceInput": True, "tooltip": "Dynamic filename (no extension). Takes priority."}),
            },
        }

    def run(self, video_path, output_name, filename_template, include, filename=""):
        if not include or not video_path:
            return {"ui": {"videos": []}, "result": (video_path,)}

        import folder_paths

        out_dir = folder_paths.get_output_directory()
        src = video_path
        if not os.path.isabs(src) or not os.path.exists(src):
            candidate = os.path.join(out_dir, os.path.basename(video_path))
            if os.path.exists(candidate):
                src = candidate
        if not os.path.exists(src):
            raise FileNotFoundError(
                f"SwordfishVideoOutput '{output_name}': video '{video_path}' not found."
            )

        ext = os.path.splitext(src)[1].lstrip(".").lower() or "mp4"
        basename = _resolve_basename(filename, filename_template, output_name)
        fname, fpath = _unique_path(out_dir, basename, ext)
        if os.path.abspath(src) != os.path.abspath(fpath):
            shutil.copyfile(src, fpath)

        return {
            "ui": {"videos": [{"filename": fname, "subfolder": "", "type": "output"}]},
            "result": (fname,),
        }
