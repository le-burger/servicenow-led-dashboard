# display/backends/sim_pygame.py
import pygame
from PIL import Image
from .base import DisplayBackend

class PygameSimulatorBackend(DisplayBackend):
    def __init__(self, width: int, height: int, scale: int = 10, title="LED Simulator"):
        super().__init__(width, height)
        self.scale = scale
        pygame.init()
        self.surface = pygame.display.set_mode((width * scale, height * scale))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

    def show(self, frame: Image.Image) -> None:
        # Handle window close events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                raise SystemExit

        if frame.mode != "RGB":
            frame = frame.convert("RGB")
        # Convert to pygame surface (fast path via string buffer)
        raw = frame.tobytes()
        surf = pygame.image.fromstring(raw, frame.size, "RGB")
        # Scale up to “big pixels”
        surf = pygame.transform.scale(surf, (self.width * self.scale, self.height * self.scale))
        self.surface.blit(surf, (0, 0))
        pygame.display.flip()
        self.clock.tick(60)  # cap redraws; not critical

    def close(self) -> None:
        pygame.quit()