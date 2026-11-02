"""
History manager for PDF Unlocker MVP 1.0 (PRD Section 2.4, FR-10, FR-11, Section 11.1).
Stores ONLY non-sensitive operation metadata when local history is enabled by the user.
Never stores plaintext passwords, candidate lists, or full filesystem paths on disk.
"""

import json
from pathlib import Path
from datetime import datetime


REDACTED_PASSWORD_LABEL = "[Masqué — Non conservé sur disque]"
REDACTED_PATH_LABEL = "[Chemin local masqué]"


class HistoryManager:
    def __init__(self, history_file: str = "history.json"):
        self.history_file = Path(history_file)
        self.items = self._load()

    def _sanitize_items(self, raw_items: list) -> list:
        sanitized = []
        changed = False
        for idx, item in enumerate(raw_items):
            if not isinstance(item, dict):
                continue
            pwd_val = item.get("password", "")
            path_val = item.get("filepath", "")
            fname_val = Path(item.get("filename", "document.pdf")).name

            if pwd_val != REDACTED_PASSWORD_LABEL or path_val != REDACTED_PATH_LABEL:
                changed = True

            sanitized.append({
                "id": item.get("id", idx + 1),
                "filename": fname_val,
                "filepath": REDACTED_PATH_LABEL,
                "password": REDACTED_PASSWORD_LABEL,
                "status": item.get("status", "Déverrouillé"),
                "duration": item.get("duration", "00:00:00"),
                "attempts": int(item.get("attempts", 1)),
                "date": item.get("date", "")
            })
        if changed:
            try:
                with open(self.history_file, "w", encoding="utf-8") as f:
                    json.dump(sanitized, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
        return sanitized

    def _load(self):
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
                return self._sanitize_items(raw if isinstance(raw, list) else [])
        except Exception:
            return []

    def save(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur d'enregistrement d'historique : {e}")

    def add_entry(self, filepath: str, password: str, duration_str: str, attempts: int, enabled: bool = True):
        """
        Ajoute une entrée non sensible à l'historique local (uniquement si activé).
        Conformément au PRD (FR-10, FR-11, Section 11.1), ni le mot de passe ni le chemin
        complet ne sont écrits sur le disque.
        """
        if not enabled:
            return None

        entry = {
            "id": len(self.items) + 1,
            "filename": Path(filepath).name,
            "filepath": REDACTED_PATH_LABEL,
            "password": REDACTED_PASSWORD_LABEL,
            "status": "Déverrouillé",
            "duration": duration_str,
            "attempts": attempts,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        self.items.insert(0, entry)
        self.save()
        return entry

    def clear(self):
        self.items = []
        self.save()

    def get_all(self):
        return self.items
