"""
Suite de tests automatisés P0 & P1 — PDF Unlocker MVP 1.0 (Conforme au PRD Section 15 & 19).
Couvre :
  - FR-02 (P0) : Contrôle préliminaire sur corpus PDF (manquant, endommagé, non chiffré,
                 restrictions de permissions seules, verrouillé par mot de passe d'ouverture).
  - FR-03 (P0) : Validation des codes à 6 chiffres et préservation des zéros initiaux (000452).
  - FR-04 (P0) : Vérification manuelle d'un candidat (correct vs incorrect).
  - FR-05 (P0) : Export déchiffré vers un nouveau fichier, interdiction d'écraser l'original,
                 et validation post-écriture par réouverture sans mot de passe.
  - FR-06 / FR-07 (P1) : Liste de candidats, dédoublonnage et motif borné ('?').
  - FR-10 / FR-11 / FR-15 (P0) : Interdiction stricte d'écrire des secrets (mots de passe,
                                 candidats) ou chemins complets dans les logs, l'historique
                                 sur disque ou le rapport de diagnostic.
"""

import sys
import json
import tempfile
import unittest
from pathlib import Path
import pikepdf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.engine import CrackerEngine
from core.history_manager import HistoryManager


class TestPdfUnlockerMvpPrd(unittest.TestCase):
    def setUp(self):
        self.engine = CrackerEngine()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)

        # Création d'un corpus synthétique de test (PRD Section 15.2)
        # 1. PDF non chiffré
        self.unencrypted_pdf = self.tmp_path / "unencrypted.pdf"
        with pikepdf.new() as pdf:
            pdf.add_blank_page(page_size=(200, 200))
            pdf.save(str(self.unencrypted_pdf))

        # 2. PDF avec code à 6 chiffres commençant par zéro (000452)
        self.zero_lead_pdf = self.tmp_path / "zero_lead.pdf"
        with pikepdf.new() as pdf:
            pdf.add_blank_page(page_size=(200, 200))
            pdf.save(
                str(self.zero_lead_pdf),
                encryption=pikepdf.Encryption(user="000452", owner="owner_secret", R=4)
            )

        # 3. PDF avec restrictions de permissions uniquement (Owner password sans User password)
        self.permissions_only_pdf = self.tmp_path / "permissions_only.pdf"
        with pikepdf.new() as pdf:
            pdf.add_blank_page(page_size=(200, 200))
            allow = pikepdf.Permissions(extract=False, print_highres=False)
            pdf.save(
                str(self.permissions_only_pdf),
                encryption=pikepdf.Encryption(user="", owner="owner_only_999", allow=allow, R=4)
            )

        # 4. Fichier PDF endommagé / invalide
        self.corrupted_pdf = self.tmp_path / "corrupted.pdf"
        self.corrupted_pdf.write_bytes(b"%PDF-1.7\nCORRUPTED_BINARY_CONTENT_EOF")

        # 5. Fichier vide
        self.empty_pdf = self.tmp_path / "empty.pdf"
        self.empty_pdf.write_bytes(b"")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_fr03_six_digit_code_validation_and_leading_zeros(self):
        """FR-03 (P0) : Vérifie la validation des codes à 6 chiffres et la conservation des zéros initiaux."""
        ok, val = self.engine.validate_six_digit_code("000452")
        self.assertTrue(ok)
        self.assertEqual(val, "000452")

        ok0, val0 = self.engine.validate_six_digit_code("000000")
        self.assertTrue(ok0)
        self.assertEqual(val0, "000000")

        # Entrées invalides
        for bad in ["452", "1234567", "12a456", "", "   ", "-12345"]:
            is_valid, _ = self.engine.validate_six_digit_code(bad)
            self.assertFalse(is_valid, f"Le code invalide '{bad}' aurait dû être rejeté.")

    def test_fr02_preliminary_inspection_corpus(self):
        """FR-02 (P0) : Vérifie que le contrôle préliminaire distingue chaque cas du corpus."""
        # Manquant
        res_missing = self.engine.inspect_pdf_detailed(str(self.tmp_path / "inexistant.pdf"))
        self.assertFalse(res_missing["is_valid"])
        self.assertEqual(res_missing["status_code"], "missing")

        # Vide
        res_empty = self.engine.inspect_pdf_detailed(str(self.empty_pdf))
        self.assertFalse(res_empty["is_valid"])
        self.assertEqual(res_empty["status_code"], "corrupted_or_invalid")

        # Endommagé
        res_corrupt = self.engine.inspect_pdf_detailed(str(self.corrupted_pdf))
        self.assertFalse(res_corrupt["is_valid"])
        self.assertEqual(res_corrupt["status_code"], "corrupted_or_invalid")

        # Non chiffré
        res_open = self.engine.inspect_pdf_detailed(str(self.unencrypted_pdf))
        self.assertTrue(res_open["is_valid"])
        self.assertFalse(res_open["is_encrypted"])
        self.assertEqual(res_open["status_code"], "unencrypted")

        # Restrictions de permissions seules
        res_perm = self.engine.inspect_pdf_detailed(str(self.permissions_only_pdf))
        self.assertTrue(res_perm["is_valid"])
        self.assertTrue(res_perm["is_encrypted"])
        self.assertEqual(res_perm["status_code"], "permissions_only")

        # Verrouillé par mot de passe d'ouverture
        res_locked = self.engine.inspect_pdf_detailed(str(self.zero_lead_pdf))
        self.assertTrue(res_locked["is_valid"])
        self.assertTrue(res_locked["is_encrypted"])
        self.assertEqual(res_locked["status_code"], "user_password_required")

    def test_fr04_manual_candidate_verification(self):
        """FR-04 (P0) : Vérifie la différenciation entre mauvais code, code exact avec zéro initial et fichier invalide."""
        ok_wrong, _ = self.engine.verify_candidate_password(str(self.zero_lead_pdf), "452")
        self.assertFalse(ok_wrong)

        ok_right, _ = self.engine.verify_candidate_password(str(self.zero_lead_pdf), "000452")
        self.assertTrue(ok_right)

    def test_fr05_export_decrypted_never_overwrites_source_and_verifies_output(self):
        """FR-05 (P0) : Vérifie l'interdiction d'écraser la source et la validation post-écriture."""
        # 1. Tenter d'écraser le fichier source doit lever une ValueError
        with self.assertRaises(ValueError):
            self.engine.decrypt_and_save_pdf(
                str(self.zero_lead_pdf),
                "000452",
                str(self.zero_lead_pdf)
            )

        # 2. Export vers un nouveau fichier
        out_file = self.tmp_path / "zero_lead_unlocked.pdf"
        saved_path = self.engine.decrypt_and_save_pdf(
            str(self.zero_lead_pdf),
            "000452",
            str(out_file)
        )
        self.assertEqual(Path(saved_path).resolve(), out_file.resolve())
        self.assertTrue(out_file.exists())

        # 3. Vérifier que la copie s'ouvre SANS mot de passe
        with pikepdf.open(str(out_file)) as unlocked_doc:
            self.assertFalse(unlocked_doc.is_encrypted)
            self.assertEqual(len(unlocked_doc.pages), 1)

        # 4. Vérifier que le fichier source original est toujours chiffré et intact
        with self.assertRaises(pikepdf.PasswordError):
            pikepdf.open(str(self.zero_lead_pdf))

    def test_fr06_fr07_candidates_list_and_bounded_pattern(self):
        """FR-06 & FR-07 (P1) : Vérifie le dédoublonnage et le plafond des motifs bornés."""
        cands, err = self.engine.build_targeted_candidates("123456\n123456\n0004??", expand_variants=False)
        self.assertEqual(err, "")
        self.assertEqual(len(cands), 101)  # "123456" (1) + "000400".."000499" (100)
        self.assertIn("000452", cands)

        # Plafond dépassé (> 5 '?')
        cands_bad, err_bad = self.engine.build_targeted_candidates("??????")
        self.assertEqual(len(cands_bad), 0)
        self.assertIn("plafond", err_bad.lower())

    def test_fr10_fr11_fr15_zero_secrets_in_logs_history_and_diagnostics(self):
        """FR-10, FR-11 & FR-15 (P0) : Garantit qu'aucun mot de passe ni chemin complet ne fuite."""
        secret_pwd = "000452"
        collected_logs = []
        found_box = []

        cands, _ = self.engine.build_targeted_candidates(f"999999\n{secret_pwd}")
        callbacks = {
            "on_log": lambda sym, msg: collected_logs.append(f"{sym} {msg}"),
            "on_found": lambda pwd, el, att: found_box.append(pwd),
        }

        self.engine._run_candidates_search(str(self.zero_lead_pdf), cands, callbacks)
        self.assertEqual(found_box, [secret_pwd])

        # Vérifier qu'aucune ligne de log ne contient le mot de passe secret ni les candidats ni le chemin
        full_log_text = "\n".join(collected_logs)
        self.assertNotIn(secret_pwd, full_log_text)
        self.assertNotIn("999999", full_log_text)
        self.assertNotIn(str(self.tmp_path), full_log_text)

        # Vérifier que l'historique sur disque ne stocke jamais le mot de passe ni le chemin complet
        hist_file = self.tmp_path / "test_history.json"
        hm = HistoryManager(str(hist_file))
        hm.add_entry(str(self.zero_lead_pdf), secret_pwd, "00:00:01", 2, enabled=True)
        raw_disk_history = hist_file.read_text(encoding="utf-8")
        self.assertNotIn(secret_pwd, raw_disk_history)
        self.assertNotIn(str(self.tmp_path), raw_disk_history)

        # Vérifier que le rapport de diagnostic expurgé (FR-15) ne contient aucun secret ni chemin
        diag = self.engine.create_redacted_diagnostic_report(
            pdf_path=str(self.zero_lead_pdf),
            last_status="completed",
            last_duration_sec=0.2
        )
        diag_json = json.dumps(diag)
        self.assertNotIn(secret_pwd, diag_json)
        self.assertNotIn("zero_lead.pdf", diag_json)
        self.assertNotIn(str(self.tmp_path), diag_json)

    def test_offline_license_manager_verification(self):
        """Vérifie la génération et la validation cryptographique hors-ligne des clés Pro et Business."""
        from core.license_manager import LicenseManager

        pro_key = LicenseManager.generate_key(tier="PRO", seed="user@togo.tg")
        ok, tier, _ = LicenseManager.verify_key(pro_key)
        self.assertTrue(ok)
        self.assertEqual(tier, "Pro")

        biz_key = LicenseManager.generate_key(tier="BIZ", seed="entreprise@togo.tg")
        ok_b, tier_b, _ = LicenseManager.verify_key(biz_key)
        self.assertTrue(ok_b)
        self.assertEqual(tier_b, "Business")

        # Clé falsifiée rejetée
        tampered = pro_key[:-4] + "0000"
        ok_t, _, _ = LicenseManager.verify_key(tampered)
        self.assertFalse(ok_t)


if __name__ == "__main__":
    unittest.main()
