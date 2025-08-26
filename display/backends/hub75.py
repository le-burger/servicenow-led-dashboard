# display/backends/hub75.py
from PIL import Image
from .base import DisplayBackend

# Import lazily so local dev doesn't need the hardware library
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except Exception:
    RGBMatrix = None
    RGBMatrixOptions = None

class Hub75Backend(DisplayBackend):
    def __init__(self, width: int, height: int, chain_length=1, parallel=1, pwm_bits=11, brightness=80):
        super().__init__(width, height)
        if RGBMatrix is None:
            raise RuntimeError("rgbmatrix library not available on this machine.")
        opts = RGBMatrixOptions()
        opts.rows = height
        opts.cols = width
        opts.chain_length = chain_length
        opts.parallel = parallel
        opts.pwm_bits = pwm_bits
        opts.brightness = brightness
        opts.gpio_slowdown = 2
        self.matrix = RGBMatrix(options=opts)

    def show(self, frame: Image.Image) -> None:
        if frame.mode != "RGB":
            frame = frame.convert("RGB")
        self.matrix.SetImage(frame, 0, 0)