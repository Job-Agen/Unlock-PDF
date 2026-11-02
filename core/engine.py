"""
High-performance cracking, verification & export engine for PDF Unlocker MVP 1.0 (PRD Compliant).
Implements:
  - FR-01 / FR-02 : Sélection et contrôle préliminaire prudent (mot de passe d'ouverture,
                    restrictions de permissions, fichier endommagé, format non supporté).
  - FR-03 : Validation stricte des codes (ex: 6 chiffres 000000-999999 avec zéros initiaux).
  - FR-04 : Vérification manuelle d'un candidat sans écriture de secret dans le journal.
  - FR-05 : Export déchiffré vers un nouveau fichier, interdiction d'écraser la source,
            et validation post-écriture par réouverture sans mot de passe.
  - FR-06 / FR-07 / FR-08 / FR-09 : Récupération ciblée (liste, motif borné, progression, arrêt).
  - FR-10 / Section 9 : Aucun mot de passe, candidat ou chemin complet dans les logs.
  - FR-15 : Génération de rapport de diagnostic technique expurgé.
"""

import time
import re
import platform
from pathlib import Path
from datetime import datetime, timezone
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import pikepdf


APP_VERSION = "1.0.0-MVP"


class CrackerEngine:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self._stop_event = threading.Event()
        self.worker_thread = None
        self.num_threads = 4

    @staticmethod
    def validate_six_digit_code(code: str) -> tuple[bool, str]:
        """
        FR-03 & Backlog P0 : Valide un code à 6 chiffres (000000 à 999999)
        en conservant les zéros initiaux et en refusant toute entrée invalide.
        """
        if not isinstance(code, str):
            return False, "Le code doit être une chaîne de caractères."
        cleaned = code.strip()
        if len(cleaned) != 6:
            return False, "Le code à 6 chiffres doit comporter exactement 6 caractères (ex: 000452)."
        if not cleaned.isdigit() or not re.fullmatch(r"[0-9]{6}", cleaned):
            return False, "Le code à 6 chiffres ne doit contenir que des chiffres de 0 à 9."
        return True, cleaned

    @staticmethod
    def get_size_bracket(size_bytes: int) -> str:
        """Retourne une tranche de taille anonymisée pour l'analytique/diagnostic (PRD 14.1)."""
        if size_bytes < 100 * 1024:
            return "< 100 Ko"
        if size_bytes < 1024 * 1024:
            return "100 Ko - 1 Mo"
        if size_bytes < 10 * 1024 * 1024:
            return "1 Mo - 10 Mo"
        return "> 10 Mo"

    @staticmethod
    def detect_encryption_details(pdf_path: str) -> str:
        """
        Inspecte l'en-tête et le dictionnaire /Encrypt du PDF pour estimer
        le type de chiffrement (RC4, AES-128, AES-256, ou certificat).
        """
        try:
            raw = Path(pdf_path).read_bytes()
            ver_m = re.search(rb"%PDF-(\d+\.\d+)", raw[:1024])
            pdf_ver = ver_m.group(1).decode("ascii", errors="ignore") if ver_m else "1.x"

            if b"/PubSec" in raw or b"/adbe.pkcs7" in raw:
                return f"Certificat / Signature numérique (PDF {pdf_ver}) — Non pris en charge"

            v_m = re.search(rb"/V\s+(\d+)", raw)
            r_m = re.search(rb"/R\s+(\d+)", raw)
            v_val = int(v_m.group(1)) if v_m else None
            r_val = int(r_m.group(1)) if r_m else None

            if v_val == 5 or (r_val and r_val >= 5):
                return f"AES-256 (PDF {pdf_ver}, R={r_val or 5}) — Chiffrement fort (vitesse réduite)"
            elif v_val == 4 or r_val == 4:
                return f"AES-128 / RC4-128 (PDF {pdf_ver}, R=4) — Vitesse standard"
            elif v_val in (1, 2) or r_val in (2, 3):
                return f"RC4 40/128-bit (PDF {pdf_ver}, R={r_val or 3}) — Vitesse élevée"
            return f"Standard PDF {pdf_ver}"
        except Exception:
            return "Standard PDF"

    @classmethod
    def inspect_pdf_detailed(cls, pdf_path: str) -> dict:
        """
        FR-01 & FR-02 : Contrôle préliminaire complet et prudent d'un fichier PDF.
        Distingue :
          - 'missing' : fichier introuvable ou inaccessible
          - 'invalid_extension' : extension non .pdf
          - 'unencrypted' : PDF lisible sans mot de passe ni restriction
          - 'permissions_only' : PDF lisible sans mot de passe d'ouverture, mais avec
                                 restrictions de permissions (Owner password)
          - 'user_password_required' : PDF protégé par un mot de passe d'ouverture
          - 'unsupported_encryption' : Chiffrement par certificat ou algorithme non supporté
          - 'corrupted_or_invalid' : Fichier PDF endommagé, vide ou tronqué
        """
        p = Path(pdf_path)
        if not p.exists() or not p.is_file():
            return {
                "is_valid": False,
                "is_encrypted": False,
                "status_code": "missing",
                "size_str": "0 octet",
                "size_bracket": "0",
                "encryption_info": "Fichier introuvable",
                "message": "Fichier introuvable. Vérifiez que le fichier existe et que vous avez les droits de lecture."
            }

        try:
            size_bytes = p.stat().st_size
            if size_bytes < 1024:
                size_str = f"{size_bytes} octets"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} Ko"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} Mo"
        except PermissionError:
            return {
                "is_valid": False,
                "is_encrypted": False,
                "status_code": "missing",
                "size_str": "0 octet",
                "size_bracket": "0",
                "encryption_info": "Permission refusée",
                "message": "Accès refusé par le système d'exploitation. Vérifiez les permissions du fichier."
            }
        except Exception:
            size_bytes = 0
            size_str = "Taille inconnue"

        size_bracket = cls.get_size_bracket(size_bytes)

        if size_bytes == 0:
            return {
                "is_valid": False,
                "is_encrypted": False,
                "status_code": "corrupted_or_invalid",
                "size_str": "0 octet",
                "size_bracket": size_bracket,
                "encryption_info": "Fichier vide",
                "message": "Ce fichier est vide (0 octet) et ne constitue pas un document PDF valide."
            }

        enc_hint = cls.detect_encryption_details(str(p))
        if "Non pris en charge" in enc_hint:
            return {
                "is_valid": False,
                "is_encrypted": True,
                "status_code": "unsupported_encryption",
                "size_str": size_str,
                "size_bracket": size_bracket,
                "encryption_info": enc_hint,
                "message": "Ce PDF utilise une protection par certificat ou signature numérique non prise en charge."
            }

        try:
            with pikepdf.open(str(p)) as pdf:
                if pdf.is_encrypted:
                    return {
                        "is_valid": True,
                        "is_encrypted": True,
                        "status_code": "permissions_only",
                        "size_str": size_str,
                        "size_bracket": size_bracket,
                        "encryption_info": f"Restrictions de permissions uniquement ({enc_hint})",
                        "message": (
                            f"Ce document ({p.name}) s'ouvre sans mot de passe d'ouverture, "
                            "mais comporte des restrictions de permissions (impression/copie). "
                            "Vous pouvez enregistrer directement une copie libre."
                        )
                    }
                return {
                    "is_valid": True,
                    "is_encrypted": False,
                    "status_code": "unencrypted",
                    "size_str": size_str,
                    "size_bracket": size_bracket,
                    "encryption_info": "Aucune protection par mot de passe",
                    "message": "Ce fichier PDF n'est pas protégé par un mot de passe."
                }
        except pikepdf.PasswordError:
            return {
                "is_valid": True,
                "is_encrypted": True,
                "status_code": "user_password_required",
                "size_str": size_str,
                "size_bracket": size_bracket,
                "encryption_info": enc_hint,
                "message": f"Fichier protégé par mot de passe d'ouverture : {p.name} ({size_str})"
            }
        except Exception as e:
            err_str = str(e).lower()
            if "unsupported" in err_str or "public key" in err_str or "certificate" in err_str:
                return {
                    "is_valid": False,
                    "is_encrypted": True,
                    "status_code": "unsupported_encryption",
                    "size_str": size_str,
                    "size_bracket": size_bracket,
                    "encryption_info": "Méthode de chiffrement non prise en charge",
                    "message": "Ce PDF utilise une variante de chiffrement non prise en charge par le moteur."
                }
            return {
                "is_valid": False,
                "is_encrypted": False,
                "status_code": "corrupted_or_invalid",
                "size_str": size_str,
                "size_bracket": size_bracket,
                "encryption_info": "Fichier endommagé ou format invalide",
                "message": "Ce fichier est endommagé, tronqué ou n'est pas un document PDF valide."
            }

    @classmethod
    def check_pdf_status(cls, pdf_path: str):
        """
        Vérifie le statut d'un fichier PDF.
        Retourne (is_valid, is_encrypted, file_size_str, message)
        """
        info = cls.inspect_pdf_detailed(pdf_path)
        return info["is_valid"], info["is_encrypted"], info["size_str"], info["message"]

    @staticmethod
    def verify_candidate_password(pdf_path: str, password: str) -> tuple[bool, str]:
        """
        FR-04 : Vérifie un mot de passe candidat unique sur le PDF.
        Différencie code correct, code incorrect et erreur technique.
        Ne journalise jamais le mot de passe testé.
        """
        p = Path(pdf_path)
        if not p.exists():
            return False, "Le fichier PDF sélectionné est introuvable."
        if password is None or password == "":
            return False, "Veuillez saisir un mot de passe candidat à vérifier."

        try:
            with pikepdf.open(str(p), password=password):
                return True, "Mot de passe candidat valide ! Vous pouvez maintenant enregistrer une copie déchiffrée."
        except pikepdf.PasswordError:
            return False, "Ce mot de passe candidat est incorrect pour ce document PDF."
        except Exception:
            return False, "Impossible d'ouvrir ce PDF (fichier endommagé ou chiffrement non pris en charge)."

    @staticmethod
    def build_targeted_candidates(
        raw_text: str,
        expand_variants: bool = False,
        deduplicate: bool = True,
        max_limit: int = 200000
    ) -> tuple[list[str], str]:
        """
        FR-06 & FR-07 : Génère une liste de mots de passe candidats à partir d'une saisie
        multi-lignes ou séparée par virgules, avec support du motif borné '?' et des variantes.
        Retourne (candidates_list, error_message).
        """
        if not raw_text or not raw_text.strip():
            return [], "Veuillez saisir au moins un mot de passe candidat ou un motif."

        tokens = [
            t.strip()
            for t in re.split(r"[\r\n,;]+", raw_text.strip())
            if t.strip()
        ]
        if not tokens:
            return [], "Aucun candidat valide détecté."

        seen = set()
        ordered = []

        def add_cand(val: str):
            if not val or len(ordered) >= max_limit:
                return
            if deduplicate:
                if val not in seen:
                    seen.add(val)
                    ordered.append(val)
            else:
                ordered.append(val)

        # 1. Candidats exacts sans joker '?'
        for tok in tokens:
            if "?" not in tok:
                add_cand(tok)

        # 2. Développement des motifs bornés '?' (jusqu'à 5 '?')
        for tok in tokens:
            q_count = tok.count("?")
            if q_count > 5:
                return [], f"Ce motif contient {q_count} caractères inconnus '?' (plafond de sécurité : 5 soit 100 000 possibilités)."
            if q_count > 0:
                total = 10 ** q_count
                fmt = f"{{:0{q_count}d}}"
                for i in range(total):
                    digits_str = fmt.format(i)
                    d_idx = 0
                    chars = []
                    for ch in tok:
                        if ch == "?":
                            chars.append(digits_str[d_idx])
                            d_idx += 1
                        else:
                            chars.append(ch)
                    add_cand("".join(chars))

        # 3. Variantes intelligentes (si activées)
        if expand_variants:
            suffixes = [
                "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                "12", "123", "1234", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "!"
            ]
            for tok in tokens:
                if "?" in tok:
                    continue
                forms = list(dict.fromkeys([tok, tok.lower(), tok.upper(), tok.capitalize()]))
                for f in forms:
                    add_cand(f)
                    for suf in suffixes:
                        add_cand(f"{f}{suf}")
                    if len(tok) <= 6:
                        for n in range(100):
                            add_cand(f"{f}{n:02d}")

        return ordered, ""

    def start_candidates_search(
        self,
        pdf_path: str,
        candidates: list[str],
        callbacks: dict,
        num_threads: int = 4
    ):
        """
        FR-06 / FR-07 / FR-08 / FR-09 : Lance le test automatique d'une liste de candidats en arrière-plan.
        """
        if self.is_running:
            return

        self.is_running = True
        self._stop_event.clear()
        self.num_threads = max(1, num_threads)

        self.worker_thread = threading.Thread(
            target=self._run_candidates_search,
            args=(pdf_path, candidates, callbacks),
            daemon=True
        )
        self.worker_thread.start()

    def _run_candidates_search(self, pdf_path: str, candidates: list[str], callbacks: dict):
        total_passwords = max(1, len(candidates))
        start_time = time.time()
        attempts_count = 0
        found_password = None

        if callbacks.get("on_start"):
            callbacks["on_start"]()

        enc_info = self.detect_encryption_details(pdf_path)
        if callbacks.get("on_log"):
            # PRD FR-10 & Section 9 : Aucun chemin complet ni secret dans le journal
            callbacks["on_log"]("➔", f"Inspection préliminaire terminée ({enc_info})")
            callbacks["on_log"]("➔", f"Démarrage de la récupération ciblée ({total_passwords:,} candidats)...".replace(",", " "))

        last_progress_time = start_time
        last_log_milestone_time = start_time
        batch_size = 64
        idx = 0

        def test_pwd(pwd_str: str) -> bool:
            try:
                with pikepdf.open(pdf_path, password=pwd_str):
                    return True
            except pikepdf.PasswordError:
                return False
            except Exception:
                return False

        try:
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                while idx < len(candidates) and not self._stop_event.is_set():
                    batch_end = min(idx + batch_size, len(candidates))
                    batch_passwords = candidates[idx:batch_end]
                    idx = batch_end

                    if attempts_count < 4 and callbacks.get("on_log"):
                        head_slice = batch_passwords[:4 - attempts_count]
                        for offset, pwd in enumerate(head_slice, start=attempts_count + 1):
                            # PRD Section 9 & Backlog P0 : Ne jamais inscrire le candidat en clair dans les logs
                            callbacks["on_log"]("➔", f"Vérification du candidat #{offset} ...")
                            if test_pwd(pwd):
                                found_password = pwd
                                attempts_count += 1
                                break
                            else:
                                callbacks["on_log"]("✕", f"Candidat #{offset} incorrect")
                                attempts_count += 1
                        if found_password:
                            break
                        batch_passwords = batch_passwords[len(head_slice):]
                        if not batch_passwords:
                            continue

                    future_to_pwd = {executor.submit(test_pwd, p): p for p in batch_passwords}
                    for future in as_completed(future_to_pwd):
                        attempts_count += 1
                        pwd = future_to_pwd[future]
                        try:
                            if future.result():
                                found_password = pwd
                                self._stop_event.set()
                                break
                        except Exception:
                            pass
                        if self._stop_event.is_set():
                            break

                    now = time.time()
                    elapsed = now - start_time
                    speed = attempts_count / elapsed if elapsed > 0.05 else float(attempts_count)

                    if (now - last_progress_time) >= 0.08 or idx >= len(candidates):
                        last_progress_time = now
                        if callbacks.get("on_progress"):
                            callbacks["on_progress"](attempts_count, total_passwords, elapsed, speed)

                    if (now - last_log_milestone_time) >= 2.5 and not self._stop_event.is_set():
                        last_log_milestone_time = now
                        if callbacks.get("on_log"):
                            callbacks["on_log"]("⌛", f"Progression : {attempts_count:,} / {total_passwords:,} candidats testés".replace(",", " "))

        except Exception as e:
            if callbacks.get("on_error"):
                callbacks["on_error"](f"Erreur technique d'exécution : {e}")

        final_elapsed = time.time() - start_time
        final_speed = attempts_count / final_elapsed if final_elapsed > 0.05 else float(attempts_count)
        self.is_running = False

        if callbacks.get("on_progress"):
            callbacks["on_progress"](
                total_passwords if found_password else attempts_count,
                total_passwords,
                final_elapsed,
                final_speed
            )

        if found_password:
            if callbacks.get("on_log"):
                # PRD FR-10 : Ne pas écrire le mot de passe en clair dans le journal
                callbacks["on_log"]("✓", "Mot de passe valide identifié ! (Affiché dans la carte Résultat, masqué du journal)")
            if callbacks.get("on_found"):
                callbacks["on_found"](found_password, final_elapsed, attempts_count)
            if callbacks.get("on_finish"):
                callbacks["on_finish"](True, final_elapsed, attempts_count)
        else:
            if self._stop_event.is_set() and idx < len(candidates):
                if callbacks.get("on_log"):
                    callbacks["on_log"]("➔", f"Opération arrêtée proprement à {attempts_count:,} candidats testés.".replace(",", " "))
            else:
                if callbacks.get("on_log"):
                    callbacks["on_log"](
                        "✕",
                        "Aucun candidat de cette sélection n'a permis d'ouvrir le PDF (le code peut être hors de l'espace testé)."
                    )
            if callbacks.get("on_finish"):
                callbacks["on_finish"](False, final_elapsed, attempts_count)

    def start_numeric_search(self, pdf_path: str, start_val: int, end_val: int, digits: int,
                             callbacks: dict, num_threads: int = 4):
        """
        Lance la recherche numérique par motif borné en arrière-plan.
        """
        if self.is_running:
            return

        self.is_running = True
        self._stop_event.clear()
        self.num_threads = max(1, num_threads)

        self.worker_thread = threading.Thread(
            target=self._run_search,
            args=(pdf_path, start_val, end_val, digits, callbacks),
            daemon=True
        )
        self.worker_thread.start()

    def stop(self):
        """Arrête proprement la tâche en cours sans toucher au fichier source (FR-09)."""
        self.is_running = False
        self._stop_event.set()

    def _run_search(self, pdf_path: str, start_val: int, end_val: int, digits: int, callbacks: dict):
        total_passwords = max(1, end_val - start_val + 1)
        start_time = time.time()
        attempts_count = 0
        found_password = None

        if callbacks.get('on_start'):
            callbacks['on_start']()

        enc_info = self.detect_encryption_details(pdf_path)
        if callbacks.get('on_log'):
            callbacks['on_log']('➔', f"Inspection préliminaire terminée ({enc_info})")
            callbacks['on_log']('✓', "Document prêt en mémoire locale")
            callbacks['on_log']('➔', f"Démarrage de la recherche bornée ({total_passwords:,} possibilités)...".replace(",", " "))

        last_progress_time = start_time
        last_log_milestone_time = start_time

        batch_size = 64
        current_val = start_val
        fmt = f"{{:0{digits}d}}"

        def test_pwd(pwd_str: str) -> bool:
            try:
                with pikepdf.open(pdf_path, password=pwd_str):
                    return True
            except pikepdf.PasswordError:
                return False
            except Exception:
                return False

        try:
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                while current_val <= end_val and not self._stop_event.is_set():
                    batch_end = min(current_val + batch_size, end_val + 1)
                    batch_passwords = [fmt.format(i) for i in range(current_val, batch_end)]
                    current_val = batch_end

                    if attempts_count < 4 and callbacks.get('on_log'):
                        head_slice = batch_passwords[:4 - attempts_count]
                        for offset, pwd in enumerate(head_slice, start=attempts_count + 1):
                            # PRD Section 9 : Ne pas logger les candidats en clair
                            callbacks['on_log']('➔', f"Vérification du candidat #{offset} ...")
                            if test_pwd(pwd):
                                found_password = pwd
                                attempts_count += 1
                                break
                            else:
                                callbacks['on_log']('✕', f"Candidat #{offset} incorrect")
                                attempts_count += 1
                        if found_password:
                            break
                        batch_passwords = batch_passwords[len(head_slice):]
                        if not batch_passwords:
                            continue

                    future_to_pwd = {executor.submit(test_pwd, p): p for p in batch_passwords}

                    for future in as_completed(future_to_pwd):
                        attempts_count += 1
                        pwd = future_to_pwd[future]
                        try:
                            if future.result():
                                found_password = pwd
                                self._stop_event.set()
                                break
                        except Exception:
                            pass

                        if self._stop_event.is_set():
                            break

                    now = time.time()
                    elapsed = now - start_time
                    speed = attempts_count / elapsed if elapsed > 0.05 else 0.0

                    if (now - last_progress_time) >= 0.08:
                        last_progress_time = now
                        if callbacks.get('on_progress'):
                            callbacks['on_progress'](attempts_count, total_passwords, elapsed, speed)

                    if (now - last_log_milestone_time) >= 2.5 and not self._stop_event.is_set():
                        last_log_milestone_time = now
                        if callbacks.get('on_log'):
                            callbacks['on_log']('⌛', f"Recherche en cours... ({attempts_count:,} candidats testés)".replace(',', ' '))

        except Exception as e:
            if callbacks.get('on_error'):
                callbacks['on_error'](f"Erreur d'exécution : {e}")

        final_elapsed = time.time() - start_time
        final_speed = attempts_count / final_elapsed if final_elapsed > 0.05 else 0.0
        self.is_running = False

        if callbacks.get('on_progress'):
            callbacks['on_progress'](attempts_count, total_passwords, final_elapsed, final_speed)

        if found_password:
            if callbacks.get('on_log'):
                callbacks['on_log']('✓', "Mot de passe valide identifié ! (Masqué dans le journal par sécurité)")
            if callbacks.get('on_found'):
                callbacks['on_found'](found_password, final_elapsed, attempts_count)
            if callbacks.get('on_finish'):
                callbacks['on_finish'](True, final_elapsed, attempts_count)
        else:
            if self._stop_event.is_set() and current_val <= end_val:
                if callbacks.get('on_log'):
                    callbacks['on_log']('➔', f"Recherche interrompue à {attempts_count:,} essais.".replace(',', ' '))
                if callbacks.get('on_finish'):
                    callbacks['on_finish'](False, final_elapsed, attempts_count)
            else:
                if callbacks.get('on_log'):
                    callbacks['on_log']('✕', "Aucun mot de passe correspondant dans la plage testée.")
                if callbacks.get('on_finish'):
                    callbacks['on_finish'](False, final_elapsed, attempts_count)

    @staticmethod
    def decrypt_and_save_pdf(pdf_path: str, password: str, output_path: str = None) -> str:
        """
        FR-05 & Backlog P0 :
        - Crée une copie déchiffrée du PDF après ouverture valide.
        - Refuse strictement d'écraser le fichier source original.
        - Vérifie post-écriture que la copie produite peut être rouverte sans mot de passe
          et qu'elle contient bien toutes les pages du document.
        Retourne le chemin du fichier enregistré et validé.
        """
        p = Path(pdf_path)
        if not p.exists():
            raise FileNotFoundError("Le fichier PDF source est introuvable.")

        if output_path is None:
            output_path = str(p.parent / f"{p.stem}_sans_mot_de_passe{p.suffix}")

        out_p = Path(output_path)
        try:
            if out_p.resolve() == p.resolve():
                raise ValueError(
                    "Sécurité FR-05 : Impossible d'écraser le fichier PDF source original. "
                    "Veuillez choisir un nouveau nom ou un autre emplacement pour la copie déchiffrée."
                )
        except ValueError:
            raise
        except Exception:
            pass

        out_p.parent.mkdir(parents=True, exist_ok=True)

        # 1. Ouverture avec le mot de passe et écriture de la copie déchiffrée
        with pikepdf.open(str(p), password=password) as src_pdf:
            expected_pages = len(src_pdf.pages)
            src_pdf.save(str(out_p))

        # 2. Validation post-écriture (FR-05 & Section 15.1 Export) :
        # Rouvrir la copie SANS mot de passe et vérifier son intégrité
        with pikepdf.open(str(out_p)) as verified_pdf:
            if verified_pdf.is_encrypted:
                raise RuntimeError("La validation post-écriture a échoué : la copie générée est encore chiffrée.")
            if len(verified_pdf.pages) != expected_pages:
                raise RuntimeError("La validation post-écriture a détecté un nombre de pages incohérent.")

        return str(out_p)

    @classmethod
    def create_redacted_diagnostic_report(
        cls,
        pdf_path: str = None,
        last_status: str = "idle",
        last_duration_sec: float = 0.0
    ) -> dict:
        """
        FR-15 & Section 14.1 : Génère un rapport technique de support 100 % expurgé.
        Ne contient aucun mot de passe, aucun candidat, aucun nom de fichier ni chemin complet.
        """
        size_bracket = "Aucun fichier"
        diag_category = "none"
        enc_summary = "N/A"

        if pdf_path and Path(pdf_path).exists():
            info = cls.inspect_pdf_detailed(pdf_path)
            size_bracket = info.get("size_bracket", "Inconnu")
            diag_category = info.get("status_code", "unknown")
            enc_summary = info.get("encryption_info", "Standard")

        return {
            "report_type": "PDF_UNLOCKER_REDACTED_DIAGNOSTIC",
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "app_version": APP_VERSION,
            "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
            "python_version": platform.python_version(),
            "pikepdf_version": getattr(pikepdf, "__version__", "unknown"),
            "document_diagnostic": {
                "status_category": diag_category,
                "size_bracket": size_bracket,
                "encryption_profile": enc_summary,
                "filepath_redacted": True,
                "secrets_redacted": True
            },
            "last_operation": {
                "status": last_status,
                "duration_seconds_bucket": (
                    "< 1s" if last_duration_sec < 1
                    else "1s - 10s" if last_duration_sec < 10
                    else "10s - 60s" if last_duration_sec < 60
                    else "> 60s"
                )
            },
            "privacy_notice": (
                "Ce rapport a été expurgé conformément au PRD (FR-10, FR-15). "
                "Aucun mot de passe, candidat, chemin complet ou contenu de PDF n'y figure."
            )
        }
