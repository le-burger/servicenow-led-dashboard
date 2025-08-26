# display/backends/image_dump.py
from pathlib import Path
from PIL import Image
from .base import DisplayBackend


class ImageDumpBackend(DisplayBackend):
    def __init__(self, width: int, height: int, out_dir="frames"):
        super().__init__(width, height)
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.counter = 0

    def show(self, frame: Image.Image) -> None:
        if frame.mode != "RGB":
            frame = frame.convert("RGB")
        self.counter += 1
        frame.save(self.out / f"frame_{self.counter:04d}.png")
