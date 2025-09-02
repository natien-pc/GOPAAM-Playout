import cv2
import numpy as np
import time

class CGObject:
    def __init__(self, visible=True, x=0, y=0, alpha=1.0):
        self.visible = visible
        self.x = x
        self.y = y
        self.alpha = alpha

    def draw(self, frame):
        return frame

    def update(self, dt):
        pass

    @staticmethod
    def _blend_image(base, overlay, x, y, alpha=1.0):
        h, w = overlay.shape[:2]
        bh, bw = base.shape[:2]
        if x < 0:
            overlay = overlay[:, -x:]
            w = overlay.shape[1]
            x = 0
        if y < 0:
            overlay = overlay[-y:, :]
            h = overlay.shape[0]
            y = 0
        if x >= bw or y >= bh:
            return base
        x2 = min(bw, x + w)
        y2 = min(bh, y + h)
        w2 = x2 - x
        h2 = y2 - y
        if w2 <= 0 or h2 <= 0:
            return base
        roi = base[y:y2, x:x2]
        overlay_roi = overlay[0:h2, 0:w2]
        if overlay_roi.shape[2] == 4:
            # use alpha channel
            alpha_mask = overlay_roi[:, :, 3] / 255.0 * alpha
            inv = 1.0 - alpha_mask
            for c in range(3):
                roi[:, :, c] = (alpha_mask * overlay_roi[:, :, c] + inv * roi[:, :, c]).astype(np.uint8)
            base[y:y2, x:x2] = roi
        else:
            cv2.addWeighted(overlay_roi, alpha, roi, 1 - alpha, 0, roi)
            base[y:y2, x:x2] = roi
        return base

class TextCG(CGObject):
    def __init__(self, text="", font=cv2.FONT_HERSHEY_SIMPLEX, scale=1.0, color=(255,255,255), thickness=2, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font = font
        self.scale = scale
        self.color = color
        self.thickness = thickness

    def draw(self, frame):
        pos = (int(self.x), int(self.y))
        cv2.putText(frame, self.text, pos, self.font, self.scale, self.color, self.thickness, cv2.LINE_AA)
        return frame

    @staticmethod
    def from_dict(d):
        return TextCG(text=d.get("text",""), x=d.get("x",10), y=d.get("y",40), alpha=d.get("alpha",1.0))

class ImageCG(CGObject):
    def __init__(self, image_path=None, **kwargs):
        super().__init__(**kwargs)
        self.img = None
        if image_path:
            self.load(image_path)

    def load(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise IOError("Cannot load image: "+str(path))
        self.img = img

    def draw(self, frame):
        if self.img is None:
            return frame
        return CGObject._blend_image(frame, self.img, int(self.x), int(self.y), alpha=self.alpha)

    @staticmethod
    def from_dict(d):
        return ImageCG(image_path=d.get("path"), x=d.get("x",0), y=d.get("y",0), alpha=d.get("alpha",1.0))

class CrawlCG(CGObject):
    def __init__(self, text="", speed=100, area_width=800, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.speed = speed  # pixels/sec
        self.offset = 0
        self.area_width = area_width
        self.last_time = None

    def update(self, dt):
        self.offset = (self.offset + self.speed * dt) % (self.area_width + 1000)

    def draw(self, frame):
        h, w = frame.shape[:2]
        y = int(self.y)
        x = int(self.x - self.offset)
        cv2.putText(frame, self.text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2, cv2.LINE_AA)
        return frame

    @staticmethod
    def from_dict(d):
        return CrawlCG(text=d.get("text",""), x=d.get("x",0), y=d.get("y",600), speed=d.get("speed",100), area_width=d.get("area_width",2000), alpha=1.0)

class ClockCG(TextCG):
    def __init__(self, fmt="%H:%M:%S", **kwargs):
        super().__init__(text="", **kwargs)
        self.fmt = fmt

    def update(self, dt):
        import datetime
        self.text = datetime.datetime.now().strftime(self.fmt)

    @staticmethod
    def from_dict(d):
        return ClockCG(fmt=d.get("fmt","%H:%M:%S"), x=d.get("x",1000), y=d.get("y",40), alpha=1.0)

class TimerCG(TextCG):
    def __init__(self, duration=0, running=False, **kwargs):
        super().__init__(text="", **kwargs)
        self.duration = duration
        self.running = running
        self.elapsed = 0

    def update(self, dt):
        if self.running:
            self.elapsed += dt
        remaining = max(0, self.duration - int(self.elapsed))
        m, s = divmod(int(remaining), 60)
        self.text = f"{m:02d}:{s:02d}"

    @staticmethod
    def from_dict(d):
        return TimerCG(duration=d.get("duration",300), running=d.get("running",False), x=d.get("x",10), y=d.get("y",40), alpha=1.0)

class ChromaCG(CGObject):
    def __init__(self, key_color=(0,255,0), threshold=60, source=None, **kwargs):
        super().__init__(**kwargs)
        self.key_color = key_color
        self.threshold = threshold
        self.source = source  # an image or frame to overlay where non-key shows

    def draw(self, frame):
        if self.source is None:
            return frame
        # simple chroma: replace key color region in source onto frame
        hsv = cv2.cvtColor(self.source, cv2.COLOR_BGR2HSV)
        key_hsv = cv2.cvtColor(np.uint8([[self.key_color]]), cv2.COLOR_BGR2HSV)[0][0]
        lower = np.array([max(0, key_hsv[0] - 10), 50, 50])
        upper = np.array([min(179, key_hsv[0] + 10), 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        mask_inv = cv2.bitwise_not(mask)
        fg = cv2.bitwise_and(self.source, self.source, mask=mask_inv)
        bg = frame.copy()
        x, y = int(self.x), int(self.y)
        h, w = fg.shape[:2]
        if y + h > bg.shape[0] or x + w > bg.shape[1]:
            # basic bounds check
            return frame
        roi = bg[y:y+h, x:x+w]
        # blend where fg non-zero
        fg_gray = cv2.cvtColor(fg, cv2.COLOR_BGR2GRAY)
        _, fg_mask = cv2.threshold(fg_gray, 1, 255, cv2.THRESH_BINARY)
        fg_mask_inv = cv2.bitwise_not(fg_mask)
        bg_part = cv2.bitwise_and(roi, roi, mask=fg_mask_inv)
        composed = cv2.add(bg_part, fg)
        bg[y:y+h, x:x+w] = composed
        return bg

    @staticmethod
    def from_dict(d):
        # source can be path to image
        inst = ChromaCG(x=d.get("x",0), y=d.get("y",0))
        path = d.get("source")
        if path:
            inst.source = cv2.imread(path, cv2.IMREAD_COLOR)
        inst.key_color = tuple(d.get("key_color", [0,255,0]))
        inst.threshold = d.get("threshold", 60)
        return inst