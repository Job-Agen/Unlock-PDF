"""
Direct Unlock & Diagnostic View (Page Déverrouiller — FR-02, FR-05, FR-15).
Allows immediate removal of a known PDF password into a verified unencrypted copy,
and generates redacted technical diagnostic reports.
"""

import os
import json
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from ui.theme import (
    COLOR_BG_ROOT, COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_PRIMARY_BLUE,
    COLOR_PRIMARY_HOVER, COLOR_SECONDARY_BTN, COLOR_SECONDARY_HOVER,
    COLOR_SUCCESS_BTN, COLOR_SUCCESS_BTN_HOVER, COLOR_CYAN,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_INPUT_BG,
    FONT_FAMILY, FONT_MONO, MAIN_MARGIN_X, MAIN_MARGIN_Y
)
from ui.icons import get_icon
from core.engine import CrackerEngine


class SearchView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_ROOT, corner_radius=0, **kwargs)
        self.direct_file_path = ""
        self.last_diagnostic = None
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=MAIN_MARGIN_X, pady=MAIN_MARGIN_Y)

        title_box = ctk.CTkFrame(container, fg_color="transparent")
        title_box.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(
            title_box,
            text="Déverrouiller un PDF",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Vous connaissez déjà le mot de passe ? Enregistrez une copie déchiffrée sans mot de passe ou inspectez le document.",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(4, 0))

        # CARD 1: Déverrouillage Direct (FR-05)
        direct_card = ctk.CTkFrame(
            container,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        direct_card.pack(fill="x", pady=(0, 18))

        d_head = ctk.CTkFrame(direct_card, fg_color="transparent")
        d_head.pack(fill="x", padx=22, pady=(18, 8))

        unlock_ic = get_icon("unlock", 18, COLOR_CYAN)
        ctk.CTkLabel(d_head, image=unlock_ic, text="").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            d_head,
            text="Créer une copie PDF déchiffrée (sans mot de passe)",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(side="left")

        ctk.CTkLabel(
            direct_card,
            text="Sélectionnez votre document PDF verrouillé et saisissez son mot de passe pour enregistrer une copie standard ouvrable librement. Le fichier original est intégralement préservé.",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=760
        ).pack(anchor="w", padx=22, pady=(0, 14))

        f_row = ctk.CTkFrame(direct_card, fg_color="transparent")
        f_row.pack(fill="x", padx=22, pady=(0, 12))

        self.direct_path_entry = ctk.CTkEntry(
            f_row,
            placeholder_text="Sélectionnez un fichier PDF protégé...",
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_FAMILY, 13),
            height=42,
            corner_radius=8
        )
        self.direct_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        folder_ic = get_icon("folder", 16, "#FFFFFF")
        choose_btn = ctk.CTkButton(
            f_row,
            text="  Choisir un fichier",
            image=folder_ic,
            compound="left",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=42,
            width=170,
            corner_radius=9,
            command=self._choose_direct_file
        )
        choose_btn.pack(side="right")

        p_row = ctk.CTkFrame(direct_card, fg_color="transparent")
        p_row.pack(fill="x", padx=22, pady=(0, 20))

        self.direct_pwd_entry = ctk.CTkEntry(
            p_row,
            placeholder_text="Mot de passe actuel du PDF...",
            show="*",
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_MONO, 13),
            height=42,
            width=260,
            corner_radius=8
        )
        self.direct_pwd_entry.pack(side="left", padx=(0, 12))

        self.show_pwd_chk = ctk.CTkCheckBox(
            p_row,
            text="Afficher",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            fg_color=COLOR_PRIMARY_BLUE,
            width=80,
            command=self._toggle_show_pwd
        )
        self.show_pwd_chk.pack(side="left", padx=(0, 16))

        save_ic = get_icon("save", 16, "#FFFFFF")
        convert_btn = ctk.CTkButton(
            p_row,
            text="  Enregistrer une copie déchiffrée",
            image=save_ic,
            compound="left",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLOR_SUCCESS_BTN,
            hover_color=COLOR_SUCCESS_BTN_HOVER,
            text_color="#FFFFFF",
            height=42,
            corner_radius=9,
            command=self._convert_direct_pdf
        )
        convert_btn.pack(side="left", fill="x", expand=True)

        # CARD 2: Diagnostic Technique Anonymisé (FR-02 & FR-15)
        diag_card = ctk.CTkFrame(
            container,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        diag_card.pack(fill="x", pady=(0, 14))

        c2_head = ctk.CTkFrame(diag_card, fg_color="transparent")
        c2_head.pack(fill="x", padx=22, pady=(18, 8))

        info_ic = get_icon("info_circle", 18, COLOR_CYAN)
        ctk.CTkLabel(c2_head, image=info_ic, text="").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            c2_head,
            text="Inspection du chiffrement & Rapport de diagnostic anonymisé",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(side="left")

        ctk.CTkLabel(
            diag_card,
            text="Vérifie l'état exact du chiffrement du document et génère un rapport JSON anonymisé (sans mot de passe ni chemin personnel).",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=760
        ).pack(anchor="w", padx=22, pady=(0, 12))

        diag_btn_row = ctk.CTkFrame(diag_card, fg_color="transparent")
        diag_btn_row.pack(fill="x", padx=22, pady=(0, 12))

        inspect_btn = ctk.CTkButton(
            diag_btn_row,
            text="Inspecter le PDF sélectionné",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            height=38,
            corner_radius=8,
            command=self._run_diagnostic
        )
        inspect_btn.pack(side="left", padx=(0, 10))

        export_diag_btn = ctk.CTkButton(
            diag_btn_row,
            text="Exporter le rapport JSON",
            font=(FONT_FAMILY, 12),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_TEXT_WHITE,
            height=38,
            corner_radius=8,
            command=self._export_diagnostic_json
        )
        export_diag_btn.pack(side="left")

        self.diag_textbox = ctk.CTkTextbox(
            diag_card,
            height=175,
            fg_color=COLOR_INPUT_BG,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_MUTED,
            font=(FONT_MONO, 12),
            corner_radius=8
        )
        self.diag_textbox.pack(fill="x", padx=22, pady=(0, 20))
        self.diag_textbox.insert("1.0", "Sélectionnez un fichier PDF ci-dessus puis cliquez sur « Inspecter le PDF sélectionné ».")

    def _choose_direct_file(self):
        f = filedialog.askopenfilename(
            title="Choisir un fichier PDF",
            filetypes=[("Fichiers PDF (*.pdf)", "*.pdf")]
        )
        if f:
            self.direct_file_path = f
            self.direct_path_entry.delete(0, "end")
            self.direct_path_entry.insert(0, f)
            self._run_diagnostic()

    def _toggle_show_pwd(self):
        if self.show_pwd_chk.get():
            self.direct_pwd_entry.configure(show="")
        else:
            self.direct_pwd_entry.configure(show="*")

    def _run_diagnostic(self):
        pdf_path = self.direct_path_entry.get().strip()
        report = CrackerEngine.create_redacted_diagnostic_report(pdf_path if pdf_path else None)
        self.last_diagnostic = report
        formatted = json.dumps(report, indent=2, ensure_ascii=False)
        self.diag_textbox.delete("1.0", "end")
        self.diag_textbox.insert("1.0", formatted)

    def _export_diagnostic_json(self):
        if not self.last_diagnostic:
            self._run_diagnostic()
        save_path = filedialog.asksaveasfilename(
            title="Enregistrer le rapport de diagnostic",
            initialfile="diagnostic_pdf_unlocker.json",
            defaultextension=".json",
            filetypes=[("Fichier JSON (*.json)", "*.json")]
        )
        if not save_path:
            return
        try:
            Path(save_path).write_text(
                json.dumps(self.last_diagnostic, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            messagebox.showinfo("Rapport exporté", f"Rapport de diagnostic enregistré :\n{save_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer le rapport : {e}")

    def _convert_direct_pdf(self):
        pdf_path = self.direct_path_entry.get().strip()
        pwd = self.direct_pwd_entry.get().strip()

        if not pdf_path or not Path(pdf_path).exists():
            messagebox.showerror("Fichier manquant", "Veuillez sélectionner un fichier PDF valide.")
            return

        if not pwd:
            messagebox.showerror("Mot de passe manquant", "Veuillez saisir le mot de passe du PDF.")
            return

        p = Path(pdf_path)
        default_name = f"{p.stem}_sans_mot_de_passe{p.suffix}"
        save_path = filedialog.asksaveasfilename(
            title="Enregistrer la copie PDF déchiffrée",
            initialdir=str(p.parent),
            initialfile=default_name,
            defaultextension=".pdf",
            filetypes=[("Fichier PDF déchiffré (*.pdf)", "*.pdf")]
        )
        if not save_path:
            return

        try:
            out_file = CrackerEngine.decrypt_and_save_pdf(pdf_path, pwd, save_path)
            ans = messagebox.askyesno(
                "Copie déchiffrée enregistrée",
                f"La copie sans mot de passe a été créée et vérifiée :\n\n{out_file}\n\n"
                "Le document original n'a pas été modifié.\n"
                "Voulez-vous ouvrir la copie déchiffrée maintenant ?"
            )
            if ans:
                os.startfile(out_file)
        except Exception as e:
            messagebox.showerror("Erreur de déchiffrement", f"Impossible de déchiffrer le PDF :\n{e}")
