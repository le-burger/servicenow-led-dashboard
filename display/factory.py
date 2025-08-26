# display/factory.py
from typing import Literal
from .backends.base import DisplayBackend
from .backends.sim_pygame import PygameSimulatorBackend
from .backends.image_dump import ImageDumpBackend

try:
    from .backends.hub75 import Hub75Backend
except Exception:
    Hub75Backend = None  # allow import on laptops


def make_display(kind: Literal["sim", "hub75", "dump"], width: int, height: int, **kwargs) -> DisplayBackend:
    if kind == "sim":
        return PygameSimulatorBackend(width, height, scale=kwargs.get("scale", 10))
    if kind == "dump":
        return ImageDumpBackend(width, height, out_dir=kwargs.get("out_dir", "frames"))
    if kind == "hub75":
        if Hub75Backend is None:
            raise RuntimeError("Hub75 backend not available on this system.")
        return Hub75Backend(width, height,
                            chain_length=kwargs.get("chain_length", 1),
                            parallel=kwargs.get("parallel", 1),
                            brightness=kwargs.get("brightness", 80))
    raise ValueError(f"Unknown display backend: {kind}")
