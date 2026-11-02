"""
Main Home View (Page Accueil) for PDF Unlocker Desktop Windows (Sections 7, 8, 9, 10, 11, 12, 13, 19).
At 1536x1024 (and >= 1180 px width): two proportional columns side by side (60% main / 40% secondary, 22 px gap).
Automatically adapts to a scrollable stacked layout on smaller windows and restores two columns when enlarged.
"""

import queue
import winsound
import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox

from ui.theme import (
    COLOR_BG_ROOT, COLOR_PRIMARY_BLUE, COLOR_PRIMARY_HOVER,
    COLOR_SECONDARY_BTN, COLOR_SECONDARY_HOVER, COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED, COLOR_NAV_INACTIVE_TEXT, FONT_FAMILY,
    MAIN_MARGIN_X, MAIN_MARGIN_Y, COLUMN_GAP
)
from ui.icons import get_icon
from ui.components.hero_banner import HeroBanner
from ui.components.file_selector import FileSelector
from ui.components.search_params import SearchParams
from ui.components.progress_card import ProgressCard
from ui.components.log_viewer import LogViewer
from ui.components.result_card import ResultCard
from core.engine import CrackerEngine
from core.history_manager import HistoryManager
from core.settings_manager import SettingsManager
from core.license_manager import LicenseManager, FREE_MAX_CANDIDATES


class HomeView(ctk.CTkFrame):
    def __init__(self, master, engine: CrackerEngine, history: HistoryManager, settings: SettingsManager, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_ROOT, corner_radius=0, **kwargs)
        self.engine = engine
        self.history = history
        self.settings = settings
        self.last_pdf_path = ""
        self.event_queue = queue.Queue()
        self._layout_mode = "two_col"  # "two_col" or "stacked"

        self._build_ui()
        self._poll_event_queue()

    def _poll_event_queue(self):
        try:
            while not self.event_queue.empty():
                evt, args = self.event_queue.get_nowait()
                if evt == 'log':
                    sym, text = args
                    self.log_viewer.add_log(sym, text)
                elif evt == 'progress':
                    cur, tot, el, sp = args
                    self.progress_card.update_metrics(cur, tot, el, sp)
                elif evt == 'found':
                    pwd, el, att, pdf_path = args
                    self._handle_found(pwd, el, att, pdf_path)
                elif evt == 'finish':
                    succ, el, att = args
                    self._handle_finish(succ, el, att)
                elif evt == 'error':
                    self.log_viewer.add_log('✕', args)
                    self.result_card.set_negative_result("Erreur technique", str(args), 0.0, 0, self.last_pdf_path)
        except Exception:
            pass
        self.after(35, self._poll_event_queue)

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Scrollable root wrapper that only scrolls when window height/width is compact
        self.workspace = ctk.CTkFrame(self, fg_color=COLOR_BG_ROOT, corner_radius=0)
        self.workspace.grid(row=0, column=0, sticky="nsew", padx=MAIN_MARGIN_X, pady=MAIN_MARGIN_Y)

        # 7.1 Proportional 2-column grid (60% main column / 40% secondary column)
        self.workspace.grid_columnconfigure(0, weight=6, uniform="home_cols")
        self.workspace.grid_columnconfigure(1, weight=4, uniform="home_cols")
        self.workspace.grid_rowconfigure(0, weight=1)

        # ==========================================
        # COLONNE PRINCIPALE (60 % — Gauche)
        # ==========================================
        self.main_col = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.main_col.grid(row=0, column=0, sticky="nsew", padx=(0, COLUMN_GAP // 2))
        self.main_col.grid_columnconfigure(0, weight=1)

        # 1. Carte de présentation (HeroBanner — Section 7.2)
        self.hero_banner = HeroBanner(self.main_col)
        self.hero_banner.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        # 2. Carte de sélection du fichier PDF (FileSelector — Section 8)
        self.file_selector = FileSelector(
            self.main_col,
            on_file_changed=self._on_file_changed,
            default_file=""
        )
        self.file_selector.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        # 3. Carte des paramètres de récupération (SearchParams — Section 9)
        self.search_params = SearchParams(self.main_col)
        self.search_params.grid(row=2, column=0, sticky="ew", pady=(0, 14))

        # 4. Boutons d'action principaux (Section 10)
        self.btn_frame = ctk.CTkFrame(self.main_col, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        self.btn_frame.grid_columnconfigure(0, weight=6)
        self.btn_frame.grid_columnconfigure(1, weight=4)

        self.play_icon = get_icon("play", 16, "#FFFFFF")
        self.start_btn = ctk.CTkButton(
            self.btn_frame,
            text="  Démarrer la récupération",
            image=self.play_icon,
            compound="left",
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=48,
            corner_radius=10,
            command=self.start_cracking
        )
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self.stop_icon = get_icon("stop", 15, COLOR_NAV_INACTIVE_TEXT)
        self.stop_btn = ctk.CTkButton(
            self.btn_frame,
            text="  Arrêter",
            image=self.stop_icon,
            compound="left",
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_NAV_INACTIVE_TEXT,
            height=48,
            corner_radius=10,
            state="disabled",
            command=self.stop_cracking
        )
        self.stop_btn.grid(row=0, column=1, sticky="ew")

        # 5. Carte de progression (ProgressCard — Section 11)
        self.progress_card = ProgressCard(self.main_col)
        self.progress_card.grid(row=4, column=0, sticky="ew")

        # ==========================================
        # COLONNE SECONDAIRE (40 % — Droite)
        # ==========================================
        self.right_col = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(COLUMN_GAP // 2, 0))
        self.right_col.grid_rowconfigure(0, weight=1)
        self.right_col.grid_rowconfigure(1, weight=0)
        self.right_col.grid_columnconfigure(0, weight=1)

        # 1. Journal des opérations (LogViewer — Section 12)
        self.log_viewer = LogViewer(self.right_col)
        self.log_viewer.grid(row=0, column=0, sticky="nsew", pady=(0, 14))

        # 2. Carte de résultat (ResultCard — Section 13)
        self.result_card = ResultCard(
            self.right_col,
            on_unlocked_saved=lambda f: self.log_viewer.add_log('✓', f"Copie déchiffrée enregistrée : {Path(f).name}")
        )
        self.result_card.grid(row=1, column=0, sticky="ew")

    def apply_responsive_layout(self, window_width: int, window_height: int):
        """
        Implements Section 19 (Window Resizing Rules):
        - Adjusts outer margins and vertical spacing progressively between 1120x760 and 1536x1024
          so both columns remain side-by-side and fully accessible down to 1120x760.
        """
        pad_x = MAIN_MARGIN_X if window_width >= 1400 else (16 if window_width >= 1240 else 12)
        pad_y = MAIN_MARGIN_Y if window_height >= 920 else (12 if window_height >= 820 else 8)
        card_gap = 14 if window_height >= 920 else (10 if window_height >= 820 else 6)

        self.workspace.grid_configure(padx=pad_x, pady=pad_y)
        self.hero_banner.grid_configure(pady=(0, card_gap))
        self.file_selector.grid_configure(pady=(0, card_gap))
        self.search_params.grid_configure(pady=(0, card_gap))
        self.btn_frame.grid_configure(pady=(0, card_gap))
        self.log_viewer.grid_configure(pady=(0, card_gap))

        is_short = window_height < 900
        is_narrow = window_width < 1340
        self.hero_banner.set_compact_vertical(is_short)
        self.file_selector.set_compact_vertical(is_short)
        self.search_params.set_compact_vertical(is_short)
        self.search_params.set_compact_labels(is_narrow)
        self.progress_card.set_compact_vertical(is_short)
        self.result_card.set_compact_labels(is_narrow)
        btn_h = 38 if is_short else 48
        self.start_btn.configure(height=btn_h)
        self.stop_btn.configure(height=btn_h)

    def _on_file_changed(self, filepath: str):
        self.last_pdf_path = filepath
        if not filepath:
            return
        info = self.engine.inspect_pdf_detailed(filepath)
        status = info.get("status")
        msg = info.get("message", "")
        if status == "user_password_required":
            self.log_viewer.add_log('✓', f"Fichier chargé avec succès ({Path(filepath).name})")
        elif status in ("unencrypted", "permissions_only"):
            self.log_viewer.add_log('ℹ', msg)
        else:
            self.log_viewer.add_log('✕', msg)

    def configure_and_run_from_recovery_page(self, method_name: str, preset_val: str = "", auto_start: bool = False):
        self.search_params.set_method(method_name, preset_val)
        if auto_start and self.file_selector.get_file():
            self.start_cracking()

    def start_cracking(self):
        if self.engine.is_running:
            return

        pdf_path = self.file_selector.get_file()
        if not pdf_path or not Path(pdf_path).exists():
            messagebox.showerror(
                "Fichier PDF requis",
                "Veuillez d'abord sélectionner un fichier PDF valide à l'aide du bouton « Choisir un fichier »."
            )
            return

        info = self.engine.inspect_pdf_detailed(pdf_path)
        if not info["is_valid"]:
            self.log_viewer.add_log('✕', info["message"])
            self.result_card.set_negative_result("Fichier PDF invalide", info["message"], 0.0, 0, pdf_path)
            messagebox.showerror("Erreur de lecture du PDF", info["message"])
            return

        if not info["is_encrypted"]:
            self.log_viewer.add_log('ℹ', info["message"])
            messagebox.showinfo("Document non verrouillé", info["message"])
            return

        method = self.search_params.current_method
        num_threads = self.settings.get("num_threads", 4) if self.search_params.use_multithread() else 1

        # Case 1: Direct single candidate verification
        if method == "Mot de passe candidat":
            pwd = self.search_params.get_context_value()
            if not pwd:
                messagebox.showwarning("Mot de passe requis", "Veuillez saisir le mot de passe candidat à vérifier.")
                return
            self.log_viewer.add_log('→', "Vérification d'un mot de passe candidat...")
            ok, msg = self.engine.verify_candidate_password(pdf_path, pwd)
            if ok:
                self.log_viewer.add_log('✓', "Mot de passe valide")
                self.progress_card.update_metrics(1, 1, 0.01, 100.0)
                self._handle_found(pwd, 0.01, 1, pdf_path)
            else:
                self.log_viewer.add_log('✕', "Mot de passe incorrect")
                self.result_card.set_negative_result(
                    "Mot de passe incorrect",
                    "Le mot de passe candidat saisi n'ouvre pas ce document.",
                    0.01,
                    1,
                    pdf_path
                )
            return

        # Case 2: Candidate list or mask (?)
        if method in ("Liste de mots de passe", "Motif partiel (?)", "Mot de passe partiellement connu (?)"):
            raw = self.search_params.get_context_value()
            candidates, err = self.engine.build_targeted_candidates(raw)
            if err or not candidates:
                messagebox.showerror("Paramètres invalides", err or "Aucun candidat valide à tester.")
                return

            lic = LicenseManager.get_license_status(self.settings)
            if not lic["is_pro"] and len(candidates) > FREE_MAX_CANDIDATES:
                ans = messagebox.askyesno(
                    "Édition Free — Limite de 50 candidats",
                    f"Votre liste génère {len(candidates):,} candidats.\n\n"
                    f"L'Édition Free permet de tester jusqu'à {FREE_MAX_CANDIDATES} candidats par opération.\n"
                    "• Cliquez sur « Oui » pour tester gratuitement les 50 premiers candidats.\n"
                    "• Cliquez sur « Non » pour activer une Licence Pro dans l'onglet Paramètres.".replace(",", " ")
                )
                if not ans:
                    return
                candidates = candidates[:FREE_MAX_CANDIDATES]

            self._set_running_ui_state(f"Recherche en cours ({len(candidates):,} candidats)...".replace(",", " "))
            callbacks = self._make_engine_callbacks(pdf_path)
            self.engine.start_candidates_search(pdf_path, candidates, callbacks, num_threads=num_threads)
            return

        # Case 3: Numeric range search
        s_val, e_val, digits, s_str, e_str = self.search_params.get_search_bounds()
        if s_val < 0 or s_val > e_val:
            messagebox.showerror(
                "Plage de recherche invalide",
                "Veuillez saisir une plage numérique valide (la valeur de départ doit être inférieure ou égale à la valeur de fin)."
            )
            return

        lic = LicenseManager.get_license_status(self.settings)
        total_range = e_val - s_val + 1
        if not lic["is_pro"] and total_range > FREE_MAX_CANDIDATES:
            ans = messagebox.askyesno(
                "Édition Free — Limite de 50 combinaisons",
                f"La plage sélectionnée comporte {total_range:,} combinaisons.\n\n"
                f"L'Édition Free permet de tester gratuitement jusqu'à {FREE_MAX_CANDIDATES} combinaisons par recherche.\n"
                f"• Cliquez sur « Oui » pour tester les {FREE_MAX_CANDIDATES} premières combinaisons ({s_str} à {str(s_val + FREE_MAX_CANDIDATES - 1).zfill(digits)}).\n"
                "• Cliquez sur « Non » pour activer une Licence Pro dans Paramètres.".replace(",", " ")
            )
            if not ans:
                return
            e_val = s_val + FREE_MAX_CANDIDATES - 1

        self._set_running_ui_state("Recherche en cours...")
        callbacks = self._make_engine_callbacks(pdf_path)
        self.engine.start_numeric_search(pdf_path, s_val, e_val, digits, callbacks, num_threads=num_threads)

    def _set_running_ui_state(self, status_text: str):
        self.start_btn.configure(state="disabled", fg_color="#124A8A")
        self.stop_btn.configure(state="normal", fg_color="#253D65", text_color=COLOR_TEXT_WHITE)
        self.progress_card.reset()
        self.progress_card.set_status_text(status_text)
        self.result_card.reset()

    def _make_engine_callbacks(self, pdf_path: str):
        return {
            'on_start': lambda: self.event_queue.put(('start', ())),
            'on_log': lambda sym, text: self.event_queue.put(('log', (sym, text))),
            'on_progress': lambda cur, tot, el, sp: self.event_queue.put(('progress', (cur, tot, el, sp))),
            'on_found': lambda pwd, el, att: self.event_queue.put(('found', (pwd, el, att, pdf_path))),
            'on_finish': lambda succ, el, att: self.event_queue.put(('finish', (succ, el, att))),
            'on_error': lambda err: self.event_queue.put(('error', err))
        }

    def stop_cracking(self):
        if self.engine.is_running:
            self.engine.stop()
            self.stop_btn.configure(state="disabled", fg_color=COLOR_SECONDARY_BTN, text_color=COLOR_NAV_INACTIVE_TEXT)
            self.progress_card.set_status_text("Arrêt en cours...")

    def _handle_found(self, password: str, elapsed: float, attempts: int, pdf_path: str):
        self.result_card.set_result(password, elapsed, attempts, pdf_path)
        self.progress_card.set_status_text("Mot de passe retrouvé !")

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.history.add_entry(
            pdf_path,
            password,
            duration_str,
            attempts,
            enabled=self.settings.get("enable_local_history", False)
        )

        if self.settings.get("play_sound", True):
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

        if self.settings.get("auto_decrypt_copy", False):
            try:
                out_path = self.engine.decrypt_and_save_pdf(pdf_path, password)
                self.result_card.decrypted_pdf_path = out_path
                self.result_card.unlocked_badge.configure(text=f"✓ Copie déchiffrée créée : {Path(out_path).name}")
                self.log_viewer.add_log('✓', f"Copie sans mot de passe créée : {Path(out_path).name}")
            except Exception as e:
                self.log_viewer.add_log('✕', f"Erreur lors de l'enregistrement déchiffré : {e}")

    def _handle_finish(self, success: bool, elapsed: float, attempts: int):
        self.start_btn.configure(state="normal", fg_color=COLOR_PRIMARY_BLUE)
        self.stop_btn.configure(state="disabled", fg_color=COLOR_SECONDARY_BTN, text_color=COLOR_NAV_INACTIVE_TEXT)
        if not success:
            if self.engine._stop_event.is_set():
                self.progress_card.set_status_text("Opération arrêtée par l'utilisateur")
                self.result_card.set_negative_result(
                    "Opération interrompue",
                    "La recherche a été arrêtée par l'utilisateur.",
                    elapsed,
                    attempts,
                    self.last_pdf_path
                )
            else:
                self.progress_card.set_status_text("Recherche terminée — Aucun code trouvé")
                self.result_card.set_negative_result(
                    "Mot de passe non trouvé",
                    "Aucune correspondance dans la plage ou liste testée.",
                    elapsed,
                    attempts,
                    self.last_pdf_path
                )
