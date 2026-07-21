"""Swordfish input nodes.

Each node exposes a single ``value`` payload widget plus the shared metadata
block. At runtime the node passes ``value`` through unchanged (Swordfish
overrides ``value`` per API call). Because the injection target is always the
Swordfish node's OWN ``value`` field, the mapping is stable and unambiguous —
it never points into a third-party node the user might swap out.

These nodes are passthrough on purpose: they can sit anywhere in the graph,
including mid-workflow to expose an intermediate value as an API knob.
"""

import os

from .common import ANY_TYPE, CATEGORY_INPUT, meta_widgets


class _SwordfishInputBase:
    CATEGORY = CATEGORY_INPUT
    FUNCTION = "run"


class SwordfishTextInput(_SwordfishInputBase):
    """String parameter (single or multi-line)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param_name": meta_widgets()["param_name"],
                "value": ("STRING", {"default": "", "multiline": True}),
                **{k: v for k, v in meta_widgets().items() if k != "param_name"},
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)

    def run(self, param_name, value, **_meta):
        return (value,)


class SwordfishIntInput(_SwordfishInputBase):
    """Integer parameter with optional min/max/step."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param_name": meta_widgets()["param_name"],
                "value": ("INT", {"default": 0, "min": -2147483648, "max": 2147483647}),
                "min": ("INT", {"default": 0, "min": -2147483648, "max": 2147483647,
                                "tooltip": "Minimum accepted value (documented + validated)."}),
                "max": ("INT", {"default": 2147483647, "min": -2147483648, "max": 2147483647,
                                "tooltip": "Maximum accepted value (documented + validated)."}),
                "step": ("INT", {"default": 1, "min": 1, "tooltip": "Step hint for the caller UI."}),
                **{k: v for k, v in meta_widgets().items() if k != "param_name"},
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)

    def run(self, param_name, value, **_meta):
        return (int(value),)


class SwordfishFloatInput(_SwordfishInputBase):
    """Float parameter with optional min/max/step."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param_name": meta_widgets()["param_name"],
                "value": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "min": ("FLOAT", {"default": 0.0, "tooltip": "Minimum accepted value."}),
                "max": ("FLOAT", {"default": 1.0, "tooltip": "Maximum accepted value."}),
                "step": ("FLOAT", {"default": 0.01, "tooltip": "Step hint for the caller UI."}),
                **{k: v for k, v in meta_widgets().items() if k != "param_name"},
            }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)

    def run(self, param_name, value, **_meta):
        return (float(value),)


class SwordfishBoolInput(_SwordfishInputBase):
    """Boolean parameter."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param_name": meta_widgets()["param_name"],
                "value": ("BOOLEAN", {"default": False}),
                **{k: v for k, v in meta_widgets().items() if k != "param_name"},
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("value",)

    def run(self, param_name, value, **_meta):
        return (bool(value),)


class SwordfishEnumInput(_SwordfishInputBase):
    """String parameter restricted to a fixed set of options.

    ``options`` is a newline-separated list; the parser turns it into the
    api_config ``options`` allowlist. ``value`` holds the current/default choice.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param_name": meta_widgets()["param_name"],
                "value": ("STRING", {"default": "", "tooltip": "Current/default choice. Should be one of the options."}),
                "options": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Allowed values, one per line. Becomes the API enum allowlist.",
                }),
                **{k: v for k, v in meta_widgets().items() if k != "param_name"},
            }
        }

    # Wildcard so the choice can drive COMBO inputs (sampler_name, scheduler,
    # ckpt_name, lora_name, ...) as well as plain STRING inputs.
    RETURN_TYPES = (ANY_TYPE,)
    RETURN_NAMES = ("value",)

    def run(self, param_name, value, options="", **_meta):
        return (value,)


class SwordfishSeedInput(_SwordfishInputBase):
    """Integer seed. When omitted at call time Swordfish can auto-randomize it."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param_name": meta_widgets(default_required=False)["param_name"],
                "value": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "randomize_if_omitted": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "If the caller omits this input, generate a fresh random seed per run.",
                }),
                **{k: v for k, v in meta_widgets(default_required=False).items() if k != "param_name"},
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)

    def run(self, param_name, value, randomize_if_omitted=True, **_meta):
        return (int(value),)


class SwordfishImageInput(_SwordfishInputBase):
    """Image parameter. Behaves like LoadImage: reads a file from the ComfyUI
    input directory named by ``value``. Swordfish writes the caller's uploaded
    bytes to that directory and sets ``value`` to the filename per request.

    Outputs (IMAGE, MASK) just like LoadImage so it drops into existing graphs.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param_name": meta_widgets()["param_name"],
                "value": ("STRING", {"default": "", "tooltip": "Filename in the input dir (set by Swordfish per call)."}),
                "accepted_formats": ("STRING", {
                    "default": "png,jpg,jpeg,webp",
                    "tooltip": "Comma-separated accepted upload formats (documentation + validation hint).",
                }),
                "max_size_mb": ("INT", {"default": 20, "min": 1, "max": 500,
                                        "tooltip": "Maximum accepted upload size in MB."}),
                **{k: v for k, v in meta_widgets().items() if k != "param_name"},
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")

    def run(self, param_name, value, accepted_formats="", max_size_mb=20, **_meta):
        import numpy as np
        import torch
        from PIL import Image, ImageOps
        import folder_paths

        path = folder_paths.get_annotated_filepath(value) if value else ""
        if not path or not os.path.exists(path):
            # Fall back to the input dir directly (Swordfish writes there).
            path = os.path.join(folder_paths.get_input_directory(), value)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"SwordfishImageInput '{param_name}': image '{value}' not found in the input directory."
            )

        img = Image.open(path)
        img = ImageOps.exif_transpose(img)  # bake orientation
        rgb = img.convert("RGB")
        arr = np.array(rgb).astype(np.float32) / 255.0
        image = torch.from_numpy(arr)[None,]

        if "A" in img.getbands():
            alpha = np.array(img.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(alpha)
        else:
            mask = torch.zeros((rgb.height, rgb.width), dtype=torch.float32)
        return (image, mask[None,])


class SwordfishVideoInput(_SwordfishInputBase):
    """Video parameter with a real decoder. Swordfish writes the caller's
    uploaded video to the input directory and sets ``value`` to the filename;
    this node decodes it (via imageio-ffmpeg) into an IMAGE frame batch + fps,
    like VHS_LoadVideo — so it drops into existing frame-based graphs.

    NOTE: audio is not extracted yet (frames + fps only).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "param_name": meta_widgets()["param_name"],
                "value": ("STRING", {"default": "", "tooltip": "Filename in the input dir (set by Swordfish per call)."}),
                "frame_load_cap": ("INT", {
                    "default": 0, "min": 0, "max": 100000,
                    "tooltip": "Max frames to load (0 = all). Guards against huge videos.",
                }),
                "accepted_formats": ("STRING", {
                    "default": "mp4,mov,webm",
                    "tooltip": "Comma-separated accepted upload formats (documentation + validation hint).",
                }),
                "max_size_mb": ("INT", {"default": 100, "min": 1, "max": 2000,
                                        "tooltip": "Maximum accepted upload size in MB."}),
                **{k: v for k, v in meta_widgets().items() if k != "param_name"},
            }
        }

    RETURN_TYPES = ("IMAGE", "FLOAT")
    RETURN_NAMES = ("frames", "fps")

    def run(self, param_name, value, frame_load_cap=0, accepted_formats="", max_size_mb=100, **_meta):
        import numpy as np
        import torch
        import imageio.v2 as imageio
        import folder_paths

        path = os.path.join(folder_paths.get_input_directory(), value) if value else ""
        if not path or not os.path.exists(path):
            raise FileNotFoundError(
                f"SwordfishVideoInput '{param_name}': video '{value}' not found in the input directory."
            )

        reader = imageio.get_reader(path, "ffmpeg")
        try:
            meta = reader.get_meta_data()
            fps = float(meta.get("fps", 24.0)) or 24.0
            frames = []
            for i, frame in enumerate(reader):
                if frame_load_cap and i >= frame_load_cap:
                    break
                frames.append(np.asarray(frame))
        finally:
            reader.close()

        if not frames:
            raise ValueError(f"SwordfishVideoInput '{param_name}': decoded zero frames from '{value}'.")

        arr = np.stack(frames).astype(np.float32) / 255.0  # [N,H,W,3]
        images = torch.from_numpy(arr)
        return (images, fps)
