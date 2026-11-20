"""A simple way to save check-ins: keep them all in one JSON file.

It looks reasonable and works fine when one person uses it at a time.
The lab shows what happens when 30 people use it at once.
"""
import json
import os


class JsonStore:
    def __init__(self, path):
        self.path = path

    def load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            # A half-written or damaged file: start over rather than crash.
            return []

    def save(self, records):
        with open(self.path, "w") as f:  # "w" empties the file before writing
            json.dump(records, f, indent=2)

    def append(self, record):
        records = self.load()
        records.append(record)
        self.save(records)
