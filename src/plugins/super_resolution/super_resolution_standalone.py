#!/usr/bin/env python3
"""
Standalone super-resolution helpers.

This module exposes a lightweight `SuperResolution` facade used by the filter
plugin as well as utility helpers for OpenCV DNN based models and
Real-ESRGAN (when the optional dependency is installed).
"""

from __future__ import annotations

import argparse
import logging
import math
import os
import re
import warnings
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import cv2
except ImportError as exc:  # pragma: no cover - dependency check
    raise ImportError(
        "OpenCV (cv2) が見つかりません。本モジュールでは必須です。"
        " `pip install opencv-python` でインストールしてください。"
    ) from exc

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover - dependency check
    raise ImportError(
        "PyTorch (torch) が見つかりません。本モジュールでは必須です。"
        " `pip install torch torchvision` でインストールしてください。"
    ) from exc

warnings.filterwarnings("ignore", category=FutureWarning)

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

_REALESRGAN_MODEL_ZOO = {
    "RealESRGAN_x4plus": {
        "scale": 4,
        "model_path": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        "net": "rrdb",
        "net_kwargs": {"num_in_ch": 3, "num_out_ch": 3, "num_feat": 64, "num_block": 23, "num_grow_ch": 32, "scale": 4},
    },
    "RealESRGAN_x4plus_anime_6B": {
        "scale": 4,
        "model_path": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
        "net": "rrdb",
        "net_kwargs": {"num_in_ch": 3, "num_out_ch": 3, "num_feat": 64, "num_block": 6, "num_grow_ch": 32, "scale": 4},
    },
    "RealESRNet_x4plus": {
        "scale": 4,
        "model_path": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRNet_x4plus.pth",
        "net": "rrdb",
        "net_kwargs": {"num_in_ch": 3, "num_out_ch": 3, "num_feat": 64, "num_block": 23, "num_grow_ch": 32, "scale": 4},
    },
    "RealESRGAN_x2plus": {
        "scale": 2,
        "model_path": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth",
        "net": "rrdb",
        "net_kwargs": {"num_in_ch": 3, "num_out_ch": 3, "num_feat": 64, "num_block": 23, "num_grow_ch": 32, "scale": 2},
    },
    "realesr-animevideov3": {
        "scale": 4,
        "model_path": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5/realesr-animevideov3.pth",
        "net": "srvgg",
        "net_kwargs": {"num_in_ch": 3, "num_out_ch": 3, "num_feat": 64, "num_conv": 32, "scale": 4},
    },
}


class ResidualBlock(nn.Module):  # type: ignore[misc]
    """Basic SRResNet residual block."""

    def __init__(self, channels: int = 64) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.prelu = nn.PReLU()
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):  # type: ignore[override]
        identity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.prelu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        return identity + out


class SRResNet(nn.Module):  # type: ignore[misc]
    """Minimal SRResNet implementation suitable for loading common checkpoints."""

    def __init__(self, upscale_factor: int = 2, num_blocks: int = 16) -> None:
        super().__init__()
        if upscale_factor not in {2, 4, 8}:
            raise ValueError("SRResNet only supports x2, x4, or x8 upscale factors.")

        self.upscale_factor = upscale_factor
        self.entry = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=9, padding=4),
            nn.PReLU(),
        )

        self.body = nn.Sequential(*(ResidualBlock() for _ in range(num_blocks)))
        self.mid_conv = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
        )

        upsample_layers = []
        for _ in range(int(np.log2(upscale_factor))):
            upsample_layers += [
                nn.Conv2d(64, 64 * 4, kernel_size=3, padding=1),
                nn.PixelShuffle(2),
                nn.PReLU(),
            ]
        self.upsample = nn.Sequential(*upsample_layers)

        self.reconstruction = nn.Conv2d(64, 3, kernel_size=9, padding=4)

    def forward(self, x):  # type: ignore[override]
        initial = self.entry(x)
        body = self.body(initial)
        body = self.mid_conv(body)
        body = body + initial
        out = self.upsample(body)
        out = self.reconstruction(out)
        return out


def _require_torch() -> None:
    if torch is None or nn is None:
        raise ImportError(
            "PyTorch is required for SuperResolution. "
            "Install torch and torchvision as documented in README."
        )


def _ensure_opencv() -> None:
    if cv2 is None:
        raise ImportError(
            "OpenCV (cv2) is required for this operation but is not available. "
            "Install opencv-python to continue."
        )


class SuperResolution:
    """
    Thin wrapper around an SRResNet model.

    The implementation gracefully falls back to bicubic interpolation when
    no model is loaded so that callers can still upsample images even when the
    learned weights are missing.
    """

    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None) -> None:
        self.device = self._resolve_device(device)
        self.model_path = model_path
        self.model: Optional[nn.Module] = None
        self.model_scale: int = 2

        if model_path:
            self.load_model(model_path)

    @staticmethod
    def _resolve_device(device: Optional[str]) -> torch.device:
        if device:
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")


def _create_realesrgan_upsampler(
    model_name: str,
    device: "torch.device",
    scale: float = 4.0,
):
    """
    Build a RealESRGANer using known pretrained weights.
    """
    if RealESRGANer is None:  # pragma: no cover - safety
        raise ImportError("RealESRGANer is unavailable. Install realesrgan to enable this feature.")

    cfg = _REALESRGAN_MODEL_ZOO.get(model_name)
    model_path = model_name
    upsampler_scale = scale

    if cfg:
        model_path = cfg["model_path"]
        upsampler_scale = cfg["scale"]

        if cfg["net"] == "rrdb":
            from basicsr.archs.rrdbnet_arch import RRDBNet

            net = RRDBNet(**cfg["net_kwargs"])
        elif cfg["net"] == "srvgg":
            from realesrgan.archs.srvgg_arch import SRVGGNetCompact

            net = SRVGGNetCompact(**cfg["net_kwargs"])
        else:  # pragma: no cover - defensive
            raise ValueError(f"Unsupported Real-ESRGAN network type: {cfg['net']}")
    else:
        from basicsr.archs.rrdbnet_arch import RRDBNet

        net = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=int(round(max(1, scale))),
        )

    tile_size = 0 if torch.cuda.is_available() else 256
    tile_size = 0 if torch.cuda.is_available() else 256
    logger.info(
        "[Real-ESRGAN] Using model '%s' (tile=%s, scale=%.2f, device=%s)",
        model_name,
        tile_size if tile_size > 0 else "full-frame",
        scale,
        device,
    )

    upsampler_cls = LoggedRealESRGANer if RealESRGANer is not None else RealESRGANer
    upsampler = upsampler_cls(
        scale=int(round(max(1, upsampler_scale))),
        model_path=model_path,
        model=net,
        tile=tile_size,
        tile_pad=10,
        pre_pad=0,
        half=False,
        device=device,
    )
    outscale = float(scale if scale else upsampler_scale)
    return upsampler, outscale

    @staticmethod
    def _detect_scale_from_filename(path: str) -> int:
        match = re.search(r"_x(\d+)", os.path.basename(path).lower())
        if match:
            candidate = max(1, int(match.group(1)))
            for valid in (2, 4, 8):
                if candidate == valid:
                    return valid
        return 2

    def load_model(self, model_path: Optional[str] = None) -> None:
        _require_torch()
        path = model_path or self.model_path
        if not path:
            raise ValueError("Model path must be provided.")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        self.model_scale = self._detect_scale_from_filename(path)
        checkpoint = torch.load(path, map_location=self.device)
        if isinstance(checkpoint, nn.Module):
            model = checkpoint
        else:
            # Support checkpoints with 'state_dict' or raw dict of parameters.
            model = SRResNet(upscale_factor=self.model_scale)
            if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]
            elif isinstance(checkpoint, dict):
                state_dict = checkpoint
            elif hasattr(checkpoint, "state_dict"):
                state_dict = checkpoint.state_dict()
            else:
                raise TypeError(
                    "Unsupported checkpoint format. Expected nn.Module or state dict."
                )
            state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
            model.load_state_dict(state_dict, strict=False)

        model.to(self.device)
        model.eval()
        self.model = model
        self.model_path = path

    def enhance_image(
        self,
        image: np.ndarray,
        scale: float = 2.0,
        use_patches: bool = True,
        patch_size: int = 300,
    ) -> np.ndarray:
        if image is None:
            raise ValueError("Input image is None.")
        if not isinstance(image, np.ndarray):
            raise TypeError("Input image must be a NumPy array.")
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("Input image must be a HxWx3 BGR array.")

        if self.model is None:
            return self._bicubic_resize(image, scale)

        if use_patches and max(image.shape[:2]) > patch_size:
            enhanced = self._enhance_in_patches(image, patch_size)
        else:
            enhanced = self._run_model(image)

        if not np.isclose(scale, self.model_scale):
            factor = scale / float(self.model_scale)
            enhanced = self._bicubic_resize(enhanced, factor)
        return enhanced

    def enhance_file(
        self,
        input_path: str,
        output_path: str,
        scale: float = 2.0,
        use_patches: bool = True,
        patch_size: int = 300,
    ) -> None:
        _ensure_opencv()
        image = cv2.imread(input_path)
        if image is None:
            raise FileNotFoundError(f"Failed to read image: {input_path}")
        enhanced = self.enhance_image(
            image, scale=scale, use_patches=use_patches, patch_size=patch_size
        )
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cv2.imwrite(output_path, enhanced)

    def _run_model(self, image: np.ndarray) -> np.ndarray:
        _require_torch()
        _ensure_opencv()
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(rgb.astype(np.float32) / 255.0)
        tensor = tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(tensor)  # type: ignore[arg-type]

        output = output.squeeze(0).clamp(0.0, 1.0).cpu().numpy()
        output = np.transpose(output, (1, 2, 0))
        output = (output * 255.0).round().astype(np.uint8)
        return cv2.cvtColor(output, cv2.COLOR_RGB2BGR)

    def _enhance_in_patches(self, image: np.ndarray, patch_size: int) -> np.ndarray:
        h, w = image.shape[:2]
        scale = self.model_scale
        out = np.zeros((int(h * scale), int(w * scale), 3), dtype=np.uint8)

        for y in range(0, h, patch_size):
            for x in range(0, w, patch_size):
                patch = image[y : y + patch_size, x : x + patch_size]
                enhanced_patch = self._run_model(patch)
                y_scaled = int(y * scale)
                x_scaled = int(x * scale)
                out[
                    y_scaled : y_scaled + enhanced_patch.shape[0],
                    x_scaled : x_scaled + enhanced_patch.shape[1],
                ] = enhanced_patch
        return out

    @staticmethod
    def _bicubic_resize(image: np.ndarray, scale: float) -> np.ndarray:
        if scale <= 0:
            raise ValueError("Scale factor must be positive.")
        _ensure_opencv()
        if np.isclose(scale, 1.0):
            return image.copy()
        height = max(1, int(round(image.shape[0] * scale)))
        width = max(1, int(round(image.shape[1] * scale)))
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)


def create_super_resolution(model_path: str, device: Optional[str] = None) -> SuperResolution:
    """
    Convenience factory mirroring the original plugin API.

    Parameters
    ----------
    model_path:
        Path to the SRResNet checkpoint (.pth).
    device:
        Optional torch device specifier ("cuda", "cpu", etc.).
    """
    sr = SuperResolution(model_path=model_path, device=device)
    return sr


class OpenCVDNNSuperResolution:
    """Simple wrapper around cv2.dnn_superres for PB models shipped by OpenCV."""

    def __init__(self, model_name: str = "EDSR", scale: int = 2, model_path: Optional[str] = None) -> None:
        _ensure_opencv()
        self.sr = cv2.dnn_superres.DnnSuperResImpl_create()
        self.model_name = model_name.lower()
        self.scale = scale
        self.model_path = self._resolve_model_path(model_path)
        self.sr.readModel(str(self.model_path))
        self.sr.setModel(self.model_name, self.scale)

    def _resolve_model_path(self, explicit_path: Optional[str]) -> Path:
        filename = f"{self.model_name}_x{self.scale}.pb"
        if explicit_path:
            candidate = Path(explicit_path).expanduser()
            if candidate.exists():
                return candidate
            raise FileNotFoundError(
                f"Model file not found: {candidate}. "
                "Download pre-trained weights (e.g., EDSR) from "
                "https://github.com/Saafke/EDSR_Tensorflow/tree/master/models "
                "or place your custom model in a directory referenced by "
                "SR_SUPERRES_MODELS."
            )

        candidates: list[Path] = []
        env_paths = os.getenv("SR_SUPERRES_MODELS")
        if env_paths:
            for fragment in env_paths.split(os.pathsep):
                if fragment:
                    candidates.append(Path(fragment).expanduser() / filename)

        module_dir = Path(__file__).resolve().parent
        candidates.append(module_dir / "models" / filename)
        candidates.append(Path.cwd() / filename)

        for candidate in candidates:
            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            f"Model file not found: {filename}. "
            "Download the OpenCV DNN models (EDSR/FSRCNN/etc.) from "
            "https://github.com/Saafke/EDSR_Tensorflow/tree/master/models "
            "and place them under src/plugins/super_resolution/models or set "
            "the SR_SUPERRES_MODELS environment variable to point to the directory."
        )

    def enhance(self, image: np.ndarray) -> np.ndarray:
        return self.sr.upsample(image)


def opencv_dnn_super_resolution(
    image: np.ndarray, model_name: str = "EDSR", scale: int = 2, model_path: Optional[str] = None
) -> np.ndarray:
    sr = OpenCVDNNSuperResolution(model_name, scale, model_path)
    return sr.enhance(image)


try:
    from realesrgan import RealESRGANer  # type: ignore
    from realesrgan.utils import RealESRGANer as _RealESRGANerClass  # noqa: F401
    _REALESRGAN_IMPORT_ERROR: Optional[BaseException] = None
except Exception as exc:  # pragma: no cover - optional dependency
    RealESRGANer = None  # type: ignore
    _REALESRGAN_IMPORT_ERROR = exc
else:

    class LoggedRealESRGANer(RealESRGANer):  # type: ignore[misc]
        """
        Thin wrapper that routes tile processing logs through the shared logger
        instead of direct stdout prints.
        """

        def tile_process(self):  # type: ignore[override]
            if getattr(self, "tile_size", 0) <= 0:
                return super().tile_process()

            batch, channel, height, width = self.img.shape
            output_height = height * self.scale
            output_width = width * self.scale
            output_shape = (batch, channel, output_height, output_width)

            # start with black image
            self.output = self.img.new_zeros(output_shape)
            tiles_x = math.ceil(width / self.tile_size)
            tiles_y = math.ceil(height / self.tile_size)
            total_tiles = tiles_x * tiles_y

            logger.info(
                "[Real-ESRGAN] Tiled inference start (tile=%d, tiles=%d, image=%dx%d, scale=%d)",
                self.tile_size,
                total_tiles,
                width,
                height,
                self.scale,
            )

            # loop over all tiles
            for y in range(tiles_y):
                for x in range(tiles_x):
                    ofs_x = x * self.tile_size
                    ofs_y = y * self.tile_size
                    input_start_x = ofs_x
                    input_end_x = min(ofs_x + self.tile_size, width)
                    input_start_y = ofs_y
                    input_end_y = min(ofs_y + self.tile_size, height)

                    input_start_x_pad = max(input_start_x - self.tile_pad, 0)
                    input_end_x_pad = min(input_end_x + self.tile_pad, width)
                    input_start_y_pad = max(input_start_y - self.tile_pad, 0)
                    input_end_y_pad = min(input_end_y + self.tile_pad, height)

                    input_tile_width = input_end_x - input_start_x
                    input_tile_height = input_end_y - input_start_y
                    tile_idx = y * tiles_x + x + 1
                    input_tile = self.img[
                        :,
                        :,
                        input_start_y_pad:input_end_y_pad,
                        input_start_x_pad:input_end_x_pad,
                    ]

                    logger.info(
                        "[Real-ESRGAN] Tile %d/%d (x:%d-%d, y:%d-%d)",
                        tile_idx,
                        total_tiles,
                        input_start_x,
                        input_end_x,
                        input_start_y,
                        input_end_y,
                    )

                    try:
                        with torch.no_grad():
                            output_tile = self.model(input_tile)
                    except RuntimeError as error:
                        logger.error("[Real-ESRGAN] Tile %d failed: %s", tile_idx, error)
                        raise

                    output_start_x = input_start_x * self.scale
                    output_end_x = input_end_x * self.scale
                    output_start_y = input_start_y * self.scale
                    output_end_y = input_end_y * self.scale

                    output_start_x_tile = (input_start_x - input_start_x_pad) * self.scale
                    output_end_x_tile = output_start_x_tile + input_tile_width * self.scale
                    output_start_y_tile = (input_start_y - input_start_y_pad) * self.scale
                    output_end_y_tile = output_start_y_tile + input_tile_height * self.scale

                    self.output[
                        :,
                        :,
                        output_start_y:output_end_y,
                        output_start_x:output_end_x,
                    ] = output_tile[
                        :,
                        :,
                        output_start_y_tile:output_end_y_tile,
                        output_start_x_tile:output_end_x_tile,
                    ]

            logger.info("[Real-ESRGAN] Tiled inference complete")


def real_esrgan_super_resolution(
    image: np.ndarray,
    scale: int = 2,
    device: str = "cpu",
    model_name: str = "RealESRGAN_x4plus",
) -> np.ndarray:
    """
    Run Real-ESRGAN via the optional realesrgan package.
    """
    if RealESRGANer is None:
        detail = ""
        if _REALESRGAN_IMPORT_ERROR is not None:
            detail = f" (root cause: {_REALESRGAN_IMPORT_ERROR})"
        raise ImportError(
            "The 'realesrgan' package is not installed or failed to import. Install it via "
            "'pip install realesrgan' to use this helper."
            + detail
        )
    _ensure_opencv()
    import torch  # Local import to keep dependency optional

    device_torch = torch.device(device)
    upsampler, outscale = _create_realesrgan_upsampler(model_name, device_torch, scale=scale)
    result_bgr, _ = upsampler.enhance(image, outscale=outscale)
    return result_bgr


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standalone Super Resolution utility.")
    parser.add_argument("input", help="Input image path.")
    parser.add_argument("output", help="Output image path.")
    parser.add_argument("--model", required=True, help="Path to SRResNet model (.pth).")
    parser.add_argument("--scale", type=float, default=2.0, help="Upscale factor (default: 2.0).")
    parser.add_argument(
        "--device", choices=["cpu", "cuda"], default=None, help="Torch device to use (default: auto)."
    )
    parser.add_argument(
        "--no-patches", action="store_true", help="Disable patch-based processing (process entire image)."
    )
    parser.add_argument("--patch-size", type=int, default=300, help="Patch size when using patches (default: 300).")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    sr = create_super_resolution(args.model, device=args.device)
    sr.enhance_file(
        input_path=args.input,
        output_path=args.output,
        scale=args.scale,
        use_patches=not args.no_patches,
        patch_size=args.patch_size,
    )


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
