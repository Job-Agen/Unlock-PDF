"""
Settings manager for PDF Unlocker MVP 1.0 (PRD Compliant).
Stores non-sensitive user preferences in settings.json.
"""

import json
from pathlib import Path


DEFAULT_SETTINGS = {
    "num_threads": 4,
    "play_sound": True,
    "auto_decrypt_copy": False,
    "enable_local_history": False,  # PRD 11.1 & FR-11: Désactivé par défaut (opt-in)
    "language": "fr",               # PRD FR-12: FR / EN
    "license_tier": "free",         # PRD FR-13: free | premium
    "license_key": "",              # Clé de licence hors-ligne (PDFU-PRO-XXXX-XXXX-XXXX)
    "theme": "dark",
    "batch_size": 64
}


class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = Path(settings_file)
        self.settings = self._load()

    def _load(self):
        if not self.settings_file.exists():
            return DEFAULT_SETTINGS.copy()
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                res = DEFAULT_SETTINGS.copy()
                res.update(data)
                return res
        except Exception:
            return DEFAULT_SETTINGS.copy()

    def save(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur d'enregistrement des paramètres : {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
