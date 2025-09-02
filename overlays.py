import cv2
import numpy as np
import time
from cg import TextCG, ImageCG, CrawlCG, ClockCG, TimerCG, ChromaCG

class OverlayManager:
    def __init__(self):
        self.layers = []  # list of CG objects (z-order by index)
        self.last_tick = time.time()

    def configure_from_layout(self, overlay_defs):
        self.layers = []
        for d in overlay_defs:
            t = d.get("type")
            if t == "text":
                self.layers.append(TextCG.from_dict(d))
            elif t == "image":
                self.layers.append(ImageCG.from_dict(d))
            elif t == "crawl":
                self.layers.append(CrawlCG.from_dict(d))
            elif t == "clock":
                self.layers.append(ClockCG.from_dict(d))
            elif t == "timer":
                self.layers.append(TimerCG.from_dict(d))
            elif t == "chroma":
                self.layers.append(ChromaCG.from_dict(d))
            else:
                # unknown type, ignore
                pass

    def render(self, frame):
        # frame is BGR numpy array
        out = frame.copy()
        for layer in self.layers:
            if not layer.visible:
                continue
            try:
                out = layer.draw(out)
            except Exception:
                pass
        return out

    def tick(self):
        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now
        for layer in self.layers:
            try:
                layer.update(dt)
            except Exception:
                pass