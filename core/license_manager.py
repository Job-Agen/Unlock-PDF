"""
Offline Cryptographic License Manager for PDF Unlocker Desktop Windows.
Supports Free tier (manual verification + 50 candidates trial) and Pro / Business tiers.
Validates license keys offline using HMAC-SHA256 without requiring an internet connection.
"""

import hashlib
import hmac
import re
from typing import Dict, Tuple

# Secret signing salt for HMAC-SHA256 offline license verification
_LICENSE_SECRET = b"PDF_UNLOCKER_DESKTOP_WIN64_2026_MASTER_KEY_v1"

FREE_MAX_CANDIDATES = 50
FREE_MAX_BATCH_FILES = 2


class LicenseManager:
    KEY_PATTERN = re.compile(r"^PDFU-(PRO|BIZ)-([A-Z0-9]{4})-([A-Z0-9]{4})-([A-Z0-9]{4})$")

    @staticmethod
    def compute_signature(tier: str, block1: str, block2: str) -> str:
        payload = f"PDFU-{tier.upper()}-{block1.upper()}-{block2.upper()}".encode("utf-8")
        digest = hmac.new(_LICENSE_SECRET, payload, hashlib.sha256).hexdigest().upper()
        return digest[:4]

    @classmethod
    def generate_key(cls, tier: str = "PRO", seed: str = "CLIENT2026") -> str:
        """Generates a valid signed license key for the given tier ('PRO' or 'BIZ')."""
        tier_norm = "BIZ" if tier.upper().startswith("B") else "PRO"
        h = hashlib.sha256(f"{tier_norm}:{seed}".encode("utf-8")).hexdigest().upper()
        b1 = h[:4]
        b2 = h[4:8]
        sig = cls.compute_signature(tier_norm, b1, b2)
        return f"PDFU-{tier_norm}-{b1}-{b2}-{sig}"

    @classmethod
    def verify_key(cls, key_str: str) -> Tuple[bool, str, str]:
        """
        Verifies a license key offline.
        Returns (is_valid, tier_name, message).
        """
        if not key_str or not isinstance(key_str, str):
            return False, "FREE", "Aucune clé de licence saisie."

        cleaned = key_str.strip().upper()
        m = cls.KEY_PATTERN.match(cleaned)
        if not m:
            return (
                False,
                "FREE",
                "Format de clé invalide. Format attendu : PDFU-PRO-XXXX-XXXX-XXXX"
            )

        tier_code, b1, b2, sig = m.groups()
        expected_sig = cls.compute_signature(tier_code, b1, b2)
        if not hmac.compare_digest(sig, expected_sig):
            return False, "FREE", "Clé de licence invalide (signature incorrecte)."

        tier_label = "Business" if tier_code == "BIZ" else "Pro"
        return True, tier_label, f"Licence {tier_label} activée avec succès."

    @classmethod
    def get_license_status(cls, settings) -> Dict[str, object]:
        saved_key = settings.get("license_key", "")
        is_valid, tier, msg = cls.verify_key(saved_key)
        return {
            "is_pro": is_valid,
            "tier": tier if is_valid else "Free",
            "license_key": saved_key if is_valid else "",
            "message": msg if is_valid else "Édition Free (Vérification manuelle + Essai 50 candidats)",
            "max_candidates": None if is_valid else FREE_MAX_CANDIDATES,
            "max_batch_files": None if is_valid else FREE_MAX_BATCH_FILES,
        }

