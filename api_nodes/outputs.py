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


class ApiImageOutput:
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


_VIDEO_CODECS = {"mp4": "libx264", "webm": "libvpx-vp9"}


class ApiVideoOutput:
    """Encode an IMAGE frame batch into a video and return it with a controlled
    filename. Takes the frames + frame_rate, encodes via imageio-ffmpeg into the
    output directory (like VHS_VideoCombine), and registers it so the runner
    returns it. Passes the frames through so it can sit mid-graph.

    NOTE: audio muxing is not supported yet (video track only). Odd frame
    dimensions are padded to even by the encoder for codec compatibility.
    """

    CATEGORY = CATEGORY_OUTPUT
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("frames",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": ("IMAGE",),
                "output_name": ("STRING", {"default": "video"}),
                "filename_template": ("STRING", {"default": "", "tooltip": "Static filename (no extension)."}),
                "format": (["mp4", "webm"], {"default": "mp4"}),
                "frame_rate": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 240.0, "step": 1.0}),
                "quality": ("INT", {"default": 8, "min": 1, "max": 10,
                                    "tooltip": "Encoder quality (higher = better/larger)."}),
                "include": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "filename": ("STRING", {"forceInput": True, "tooltip": "Dynamic filename (no extension). Takes priority."}),
                "fps": ("FLOAT", {"forceInput": True, "tooltip": "Optional wired fps; overrides frame_rate widget."}),
            },
        }

    def run(self, frames, output_name, filename_template, format, frame_rate, quality, include, filename="", fps=None):
        if not include:
            return {"ui": {"videos": []}, "result": (frames,)}

        import numpy as np
        import imageio.v2 as imageio
        import folder_paths

        out_dir = folder_paths.get_output_directory()
        ext = format.lower()
        codec = _VIDEO_CODECS.get(ext, "libx264")
        rate = float(fps) if fps else float(frame_rate)
        basename = _resolve_basename(filename, filename_template, output_name)
        fname, fpath = _output_path(out_dir, basename, ext)

        writer = imageio.get_writer(
            fpath, fps=rate, codec=codec, quality=quality, macro_block_size=2,
        )
        try:
            batch = frames.shape[0] if hasattr(frames, "shape") else len(frames)
            for i in range(batch):
                arr = 255.0 * frames[i].cpu().numpy()
                writer.append_data(np.clip(arr, 0, 255).astype(np.uint8))
        finally:
            writer.close()

        return {
            "ui": {"videos": [{"filename": fname, "subfolder": "", "type": "output"}]},
            "result": (frames,),
        }
