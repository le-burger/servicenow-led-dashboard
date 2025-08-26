# display/backends/base.py
from PIL import Image
from abc import ABC, abstractmethod


class DisplayBackend(ABC):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @abstractmethod
    def show(self, frame: Image.Image) -> None:
        """Blit an RGB Pillow Image of size (width, height) to the display."""
        ...

    def close(self) -> None:
        """Optional cleanup (window close, hardware release)."""
        pass
