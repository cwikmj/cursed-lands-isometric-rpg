import time
from settings import *

class GameLog:
    def __init__(self):
        self.max_lines = LOG_MAX_LINES
        self.line_lifetime = LOG_MAX_DURATION
        self.lines = []

    def add_line(self, text):
        timestamp = time.time()
        self.lines.append((text, timestamp))
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)

    def update(self):
        now = time.time()
        self.lines = [(text, ts) for text, ts in self.lines if now - ts <= self.line_lifetime]

    def get_lines(self):
        return [text for text, ts in self.lines]

    def get_message_for_item(self, item):
        msg = {
            "loot": f"Found {item.value} gold pieces",
            "potion": f"Found {item.name.capitalize()} potion"
        }
        return msg.get(item.type, f"Found {item.name}")