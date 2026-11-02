"""
Batch Processing View (Page Traitement par lots — Section 15 of Master Prompt & Reference Images 1/2/3).
Includes:
- 15.1 Add zone with upload icon, file count indicator, and 'Ajouter des fichiers' button.
- 15.2 File table with columns: Fichier | Taille | Statut | Résultat | Action (Ouvrir / Retirer).
- 15.3 Actions: 'Ajouter des fichiers', 'Retirer la sélection', 'Démarrer le traitement', 'Arrêter'.
Processes files sequentially using the real CrackerEngine.
"""

import os
import threading
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from ui.theme import (
    COLOR_BG_ROOT, COLOR_CARD_BG, COLOR_CARD_SECONDARY, COLOR_CARD_BORDER,
    COLOR_PRIMARY_BLUE, COLOR_PRIMARY_HOVER, COLOR_SECONDARY_BTN, COLOR_SECONDARY_HOVER,
    COLOR_SUCCESS_TEXT, COLOR_ERROR_RED, COLOR_WARNING_AMBER, COLOR_CYAN,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_DIM, COLOR_INPUT_BG,
    FONT_FAMILY, FONT_MONO, MAIN_MARGIN_X, MAIN_MARGIN_Y
)
from ui.icons import get_icon
from core.engine import CrackerEngine


class BatchView(ctk.CTkFrame):
    def __init__(self, master, engine: CrackerEngine, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_ROOT, corner_radius=0, **kwargs)
        self.engine = engine
        self.batch_items = []  # List of dicts: {path, name, size_str, status, result, valid, encrypted}
        self.is_batch_running = False
        self._stop_batch = threading.Event()
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=MAIN_MARGIN_X, pady=(MAIN_MARGIN_Y, 14))
        header.grid_columnconfigure(0, weight=1)

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_col,
            text="Traitement par lots",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col,
            text="Vérifiez et déverrouillez plusieurs fichiers PDF en une seule opération séquentielle.",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(3, 0))

        # 15.1 Add Zone Card
        add_zone = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD_SECONDARY,
            corner_radius=13,
            border_width=1,
            border_color="#234C9A"
        )
        add_zone.grid(row=1, column=0, sticky="ew", padx=MAIN_MARGIN_X, pady=(0, 14))
        add_zone.grid_columnconfigure(1, weight=1)

        up_ic = get_icon("upload_folder", 34, COLOR_CYAN)
        ctk.CTkLabel(add_zone, image=up_ic, text="").grid(row=0, column=0, rowspan=2, padx=(22, 16), pady=18)

        zone_txt = ctk.CTkFrame(add_zone, fg_color="transparent")
        zone_txt.grid(row=0, column=1, rowspan=2, sticky="w", pady=16)

        ctk.CTkLabel(
            zone_txt,
            text="Sélectionnez un ou plusieurs fichiers PDF à traiter",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w")

        self.count_lbl = ctk.CTkLabel(
            zone_txt,
            text="0 document sélectionné • Candidats testés sur chaque PDF verrouillé",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED
        )
        self.count_lbl.pack(anchor="w", pady=(2, 0))

        # Batch candidates input + Add buttons
        right_ctrl = ctk.CTkFrame(add_zone, fg_color="transparent")
        right_ctrl.grid(row=0, column=2, rowspan=2, padx=22, pady=16, sticky="e")

        ctk.CTkLabel(
            right_ctrl,
            text="Candidats / Motif à tester :",
            font=(FONT_FAMILY, 11),
            text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.batch_cands_entry = ctk.CTkEntry(
            right_ctrl,
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_MONO, 12),
            width=210,
            height=38,
            corner_radius=8
        )
        self.batch_cands_entry.insert(0, "123456, 000452, 4827??")
        self.batch_cands_entry.grid(row=0, column=1, padx=(0, 12))

        folder_ic = get_icon("folder", 16, "#FFFFFF")
        self.add_btn = ctk.CTkButton(
            right_ctrl,
            text="  Ajouter des fichiers",
            image=folder_ic,
            compound="left",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=38,
            corner_radius=9,
            command=self._add_files
        )
        self.add_btn.grid(row=0, column=2)

        # 15.2 Table Card
        table_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        table_card.grid(row=2, column=0, sticky="nsew", padx=MAIN_MARGIN_X, pady=(0, 14))
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        # Table Header Row
        thead = ctk.CTkFrame(table_card, fg_color="#081427", corner_radius=8, height=40)
        thead.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 6))
        thead.grid_propagate(False)
        thead.grid_columnconfigure(0, weight=4, uniform="bcols")
        thead.grid_columnconfigure(1, weight=2, uniform="bcols")
        thead.grid_columnconfigure(2, weight=3, uniform="bcols")
        thead.grid_columnconfigure(3, weight=3, uniform="bcols")
        thead.grid_columnconfigure(4, weight=2, uniform="bcols")

        headers = ["Fichier", "Taille", "Statut", "Résultat", "Action"]
        for i, h_text in enumerate(headers):
            ctk.CTkLabel(
                thead,
                text=h_text,
                font=(FONT_FAMILY, 12, "bold"),
                text_color=COLOR_TEXT_MUTED,
                anchor="w"
            ).grid(row=0, column=i, sticky="ew", padx=14, pady=8)

        self.rows_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.rows_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.rows_scroll.grid_columnconfigure(0, weight=1)

        # 15.3 Bottom Action Bar
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.grid(row=3, column=0, sticky="ew", padx=MAIN_MARGIN_X, pady=(0, MAIN_MARGIN_Y))
        action_bar.grid_columnconfigure(2, weight=1)

        self.add_bottom_btn = ctk.CTkButton(
            action_bar,
            text="Ajouter des fichiers",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_TEXT_WHITE,
            height=44,
            width=170,
            corner_radius=9,
            command=self._add_files
        )
        self.add_bottom_btn.grid(row=0, column=0, padx=(0, 10))

        self.clear_sel_btn = ctk.CTkButton(
            action_bar,
            text="Retirer la sélection",
            font=(FONT_FAMILY, 13),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_TEXT_MUTED,
            height=44,
            width=165,
            corner_radius=9,
            command=self._clear_all
        )
        self.clear_sel_btn.grid(row=0, column=1)

        play_ic = get_icon("play", 16, "#FFFFFF")
        self.start_batch_btn = ctk.CTkButton(
            action_bar,
            text="  Démarrer le traitement",
            image=play_ic,
            compound="left",
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=46,
            width=240,
            corner_radius=10,
            command=self._start_batch
        )
        self.start_batch_btn.grid(row=0, column=3, padx=(0, 10))

        stop_ic = get_icon("stop", 15, COLOR_TEXT_MUTED)
        self.stop_batch_btn = ctk.CTkButton(
            action_bar,
            text="  Arrêter",
            image=stop_ic,
            compound="left",
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_TEXT_MUTED,
            height=46,
            width=140,
            corner_radius=10,
            state="disabled",
            command=self._stop_batch_run
        )
        self.stop_batch_btn.grid(row=0, column=4)

        self._render_table()

    def _add_files(self):
        if self.is_batch_running:
            return
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers PDF",
            filetypes=[("Fichiers PDF (*.pdf)", "*.pdf")]
        )
        if not files:
            return

        existing = {item["path"] for item in self.batch_items}
        for f in files:
            if f in existing:
                continue
            info = CrackerEngine.inspect_pdf_detailed(f)
            st = info.get("status")
            if st == "user_password_required":
                status_label = "En attente"
                res_label = "--"
            elif st in ("unencrypted", "permissions_only"):
                status_label = "Non verrouillé"
                res_label = "Aucun code requis"
            else:
                status_label = "Fichier invalide"
                res_label = "Erreur de lecture"

            self.batch_items.append({
                "path": f,
                "name": Path(f).name,
                "size_str": info.get("size_str", "--").replace(".", ","),
                "status": status_label,
                "result": res_label,
                "valid": info.get("is_valid", False),
                "encrypted": info.get("is_encrypted", False),
            })

        self._render_table()

    def _remove_item(self, idx: int):
        if self.is_batch_running:
            return
        if 0 <= idx < len(self.batch_items):
            self.batch_items.pop(idx)
            self._render_table()

    def _clear_all(self):
        if self.is_batch_running:
            return
        self.batch_items.clear()
        self._render_table()

    def _render_table(self):
        for w in self.rows_scroll.winfo_children():
            w.destroy()

        n = len(self.batch_items)
        self.count_lbl.configure(
            text=f"{n} document{'s' if n > 1 else ''} sélectionné{'s' if n > 1 else ''} • Traitement séquentiel sécurisé"
        )

        if not self.batch_items:
            empty = ctk.CTkFrame(self.rows_scroll, fg_color="transparent")
            empty.grid(row=0, column=0, sticky="ew", pady=48)
            ctk.CTkLabel(
                empty,
                text="Aucun fichier dans la file de traitement — Cliquez sur « Ajouter des fichiers ».",
                font=(FONT_FAMILY, 13),
                text_color=COLOR_TEXT_DIM
            ).pack()
            return

        for idx, item in enumerate(self.batch_items):
            bg = "#0E213E" if idx % 2 == 1 else "transparent"
            row = ctk.CTkFrame(self.rows_scroll, fg_color=bg, corner_radius=8, height=44)
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=4, uniform="bcols")
            row.grid_columnconfigure(1, weight=2, uniform="bcols")
            row.grid_columnconfigure(2, weight=3, uniform="bcols")
            row.grid_columnconfigure(3, weight=3, uniform="bcols")
            row.grid_columnconfigure(4, weight=2, uniform="bcols")

            disp_name = item["name"] if len(item["name"]) <= 32 else item["name"][:29] + "..."
            ctk.CTkLabel(row, text=disp_name, font=(FONT_FAMILY, 13, "bold"), text_color=COLOR_TEXT_WHITE, anchor="w").grid(row=0, column=0, sticky="ew", padx=14, pady=8)
            ctk.CTkLabel(row, text=item["size_str"], font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED, anchor="w").grid(row=0, column=1, sticky="ew", padx=14, pady=8)

            st = item["status"]
            st_col = COLOR_TEXT_MUTED
            if st == "Terminé":
                st_col = COLOR_SUCCESS_TEXT
            elif st == "En cours...":
                st_col = COLOR_CYAN
            elif st in ("Échec", "Fichier invalide"):
                st_col = COLOR_ERROR_RED
            elif st == "Non verrouillé":
                st_col = COLOR_WARNING_AMBER

            ctk.CTkLabel(row, text=st, font=(FONT_FAMILY, 12, "bold"), text_color=st_col, anchor="w").grid(row=0, column=2, sticky="ew", padx=14, pady=8)

            res_col = COLOR_SUCCESS_TEXT if st == "Terminé" else COLOR_TEXT_MUTED
            ctk.CTkLabel(row, text=item["result"], font=(FONT_MONO, 12, "bold"), text_color=res_col, anchor="w").grid(row=0, column=3, sticky="ew", padx=14, pady=8)

            act_frame = ctk.CTkFrame(row, fg_color="transparent")
            act_frame.grid(row=0, column=4, sticky="w", padx=10)

            ctk.CTkButton(
                act_frame,
                text="Ouvrir",
                font=(FONT_FAMILY, 11),
                fg_color=COLOR_SECONDARY_BTN,
                hover_color=COLOR_SECONDARY_HOVER,
                width=58,
                height=28,
                corner_radius=6,
                command=lambda p=item["path"]: self._open_file(p)
            ).pack(side="left", padx=(0, 6))

            trash_ic = get_icon("trash", 14, COLOR_ERROR_RED)
            ctk.CTkButton(
                act_frame,
                text="",
                image=trash_ic,
                fg_color="transparent",
                hover_color="#2A0E17",
                width=30,
                height=28,
                corner_radius=6,
                command=lambda i=idx: self._remove_item(i)
            ).pack(side="left")

    def _open_file(self, path: str):
        if path and Path(path).exists():
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

    def _start_batch(self):
        if self.is_batch_running or not self.batch_items:
            return

        raw = self.batch_cands_entry.get().strip()
        candidates, err = CrackerEngine.build_targeted_candidates(raw)
        if err or not candidates:
            messagebox.showerror("Candidats invalides", err or "Veuillez saisir une liste ou un motif valide.")
            return

        self.is_batch_running = True
        self._stop_batch.clear()
        self.start_batch_btn.configure(state="disabled")
        self.stop_batch_btn.configure(state="normal", text_color=COLOR_TEXT_WHITE)

        threading.Thread(target=self._batch_worker, args=(candidates,), daemon=True).start()

    def _stop_batch_run(self):
        self._stop_batch.set()
        self.engine.stop()

    def _batch_worker(self, candidates):
        for idx, item in enumerate(self.batch_items):
            if self._stop_batch.is_set():
                break
            if not item["valid"] or not item["encrypted"]:
                continue

            item["status"] = "En cours..."
            self.after(0, self._render_table)

            found_pwd = None
            for cand in candidates:
                if self._stop_batch.is_set():
                    break
                ok, _ = CrackerEngine.verify_candidate_password(item["path"], cand)
                if ok:
                    found_pwd = cand
                    break

            if found_pwd is not None:
                item["status"] = "Terminé"
                item["result"] = found_pwd
            elif self._stop_batch.is_set():
                item["status"] = "Interrompu"
                item["result"] = "Arrêté"
            else:
                item["status"] = "Échec"
                item["result"] = "Non trouvé"

            self.after(0, self._render_table)

        self.is_batch_running = False
        self.after(0, self._on_batch_complete)

    def _on_batch_complete(self):
        self.start_batch_btn.configure(state="normal")
        self.stop_batch_btn.configure(state="disabled", text_color=COLOR_TEXT_MUTED)

