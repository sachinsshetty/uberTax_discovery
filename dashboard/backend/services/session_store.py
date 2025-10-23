# File: services/session_store.py
import json
from pathlib import Path
import logging
from ..constants import SESSION_FILE

logger = logging.getLogger(__name__)

class Store:
    def __init__(self, file_path: Path = SESSION_FILE):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self.load()

    def load(self):
        if self.file_path.exists():
            try:
                return json.loads(self.file_path.read_text())
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load session store: {str(e)}")
                return {}
        return {}

    def get(self, key, default=None):
        keys = key.split('.')
        data = self.data
        for k in keys:
            data = data.get(k, {})
        return data if data != {} else default

    def set(self, key, value):
        keys = key.split('.')
        data = self.data
        for k in keys[:-1]:
            data = data.setdefault(k, {})
        data[keys[-1]] = value
        try:
            self.file_path.write_text(json.dumps(self.data, indent=2))
        except IOError as e:
            logger.error(f"Failed to save session store: {str(e)}")

# Global instance
session_store = Store()