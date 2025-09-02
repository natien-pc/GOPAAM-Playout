import feedparser
import threading
import time

class RSSReader:
    def __init__(self, url, interval=60):
        self.url = url
        self.interval = interval
        self.items = []
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)

    def _run(self):
        while self.running:
            try:
                d = feedparser.parse(self.url)
                entries = [e.title for e in d.entries[:20]]
                self.items = entries
            except Exception:
                pass
            time.sleep(self.interval)

    def get_items(self):
        return list(self.items)