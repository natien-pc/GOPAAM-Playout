import cv2
import threading
import time

class VideoPlayer:
    def __init__(self):
        self.cap = None
        self.running = False
        self.playing = False
        self.frame_callback = None
        self.thread = None
        self.lock = threading.Lock()

    def set_frame_callback(self, cb):
        self.frame_callback = cb

    def open(self, source):
        self.stop()
        # source can be path or stream URL
        self.cap = cv2.VideoCapture(source)
        if not self.cap or not self.cap.isOpened():
            raise IOError("Cannot open source: " + str(source))

    def play(self):
        with self.lock:
            if self.playing:
                return
            self.playing = True
            if not self.thread or not self.thread.is_alive():
                self.running = True
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()

    def pause(self):
        with self.lock:
            self.playing = False

    def stop(self):
        self.running = False
        self.playing = False
        if self.thread:
            self.thread.join(timeout=0.5)
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None

    def is_playing(self):
        return self.playing

    def _run(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
        delay = 1.0 / max(1.0, fps)
        while self.running and self.cap and self.cap.isOpened():
            if not self.playing:
                time.sleep(0.05)
                continue
            ret, frame = self.cap.read()
            if not ret:
                # try to loop or stop
                self.running = False
                break
            if self.frame_callback:
                try:
                    self.frame_callback(frame)
                except Exception:
                    pass
            time.sleep(delay)