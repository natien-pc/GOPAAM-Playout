# Simple SMS moderation queue skeleton.
# Replace the enqueue/approve logic with real SMS provider webhooks.

class SMSModeration:
    def __init__(self):
        # A simple in-memory queue of strings
        self.queue = []
        # preload with example messages
        self.queue.extend([
            "Hello from viewer 1",
            "Promote the new show!",
            "Congrats on the special edition"
        ])

    def enqueue(self, text):
        self.queue.append(text)

    def approve(self, text):
        # In production, this would forward to on-air CG or playout system
        print("Approved SMS for on-air:", text)
        if text in self.queue:
            self.queue.remove(text)

    def reject(self, text):
        if text in self.queue:
            self.queue.remove(text)

    def preview_items(self):
        return list(self.queue)