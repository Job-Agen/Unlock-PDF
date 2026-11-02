"""
Result Card component for PDF Unlocker Desktop Windows (Section 13 of Master Prompt).
Supports:
- Neutral idle state (never displays a fake password!)
- Positive result state (#062A28 background, #087C5A border, #16D18C 32px bold code, real stats)
- Negative / error state (#2A0E17 background, #FF5368 text, clear distinction between wrong password and read error)
- Post-success actions: 'Ouvrir le PDF', 'Enregistrer une copie déchiffrée', 'Copier le mot de passe'.
"""

import os
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from ui.theme import (
    COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_INPUT_BG,
    COLOR_SUCCESS_BG, COLOR_SUCCESS_BORDER, COLOR_SUCCESS_TEXT,
    COLOR_SUCCESS_BTN, COLOR_SUCCESS_BTN_HOVER,
    COLOR_ERROR_BG, COLOR_ERROR_BORDER, COLOR_ERROR_RED,
    COLOR_PRIMARY_BLUE, COLOR_PRIMARY_HOVER,
    COLOR_SECONDARY_BTN, COLOR_SECONDARY_HOVER,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    FONT_FAMILY, FONT_MONO, FONT_SIZE_RESULT_VALUE
)
from ui.icons import get_icon
from core.engine import CrackerEngine


class ResultCard(ctk.CTkFrame):
    def __init__(self, master, on_unlocked_saved=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            **kwargs
        )
        self.found_password = None
        self.current_pdf_path = None
        self.decrypted_pdf_path = None
        self.on_unlocked_saved = on_unlocked_saved
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Header ("Résultat")
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))

        self.icon_ok = get_icon("check_circle", 18, COLOR_SUCCESS_TEXT)
        self.icon_err = get_icon("error_circle", 18, COLOR_ERROR_RED)
        self.icon_idle = get_icon("info_circle", 18, COLOR_TEXT_MUTED)

        self.header_icon_lbl = ctk.CTkLabel(header_frame, image=self.icon_idle, text="")
        self.header_icon_lbl.grid(row=0, column=0, padx=(0, 10))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Résultat",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE
        )
        title_lbl.grid(row=0, column=1, sticky="w")

        # Result Container Box
        self.result_box = ctk.CTkFrame(
            self,
            fg_color=COLOR_INPUT_BG,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        self.result_box.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        self.result_box.grid_columnconfigure(0, weight=1)

        box_inner = ctk.CTkFrame(self.result_box, fg_color="transparent")
        box_inner.grid(row=0, column=0, sticky="ew", padx=18, pady=14)
        box_inner.grid_columnconfigure(0, weight=1)

        self.status_subtitle = ctk.CTkLabel(
            box_inner,
            text="En attente d'une opération",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.status_subtitle.grid(row=0, column=0, sticky="w")

        # Password value (32 px bold, never shows a fake value!)
        self.pwd_display = ctk.CTkLabel(
            box_inner,
            text="------",
            font=(FONT_MONO, FONT_SIZE_RESULT_VALUE, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.pwd_display.grid(row=1, column=0, sticky="w", pady=(4, 6))

        self.doc_lbl = ctk.CTkLabel(
            box_inner,
            text="Document : --",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.doc_lbl.grid(row=2, column=0, sticky="w")

        self.time_lbl = ctk.CTkLabel(
            box_inner,
            text="Temps écoulé : --:--:--",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.time_lbl.grid(row=3, column=0, sticky="w", pady=(1, 0))

        self.attempts_lbl = ctk.CTkLabel(
            box_inner,
            text="Essais nécessaires : --",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.attempts_lbl.grid(row=4, column=0, sticky="w", pady=(1, 2))

        self.unlocked_badge = ctk.CTkLabel(
            box_inner,
            text="",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=COLOR_SUCCESS_TEXT,
            anchor="w"
        )
        self.unlocked_badge.grid(row=5, column=0, sticky="w")

        # 13.2 Action Buttons Row 1: "Ouvrir le PDF" & "Copier le mot de passe"
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        self.doc_btn_icon = get_icon("file_doc", 16, "#FFFFFF")
        self.open_btn = ctk.CTkButton(
            btn_row,
            text="  Ouvrir le PDF",
            image=self.doc_btn_icon,
            compound="left",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_SUCCESS_BTN,
            hover_color=COLOR_SUCCESS_BTN_HOVER,
            text_color="#FFFFFF",
            height=40,
            corner_radius=9,
            state="disabled",
            command=self._open_pdf
        )
        self.open_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.copy_icon = get_icon("copy", 16, COLOR_TEXT_WHITE)
        self.copy_btn = ctk.CTkButton(
            btn_row,
            text="  Copier le mot de passe",
            image=self.copy_icon,
            compound="left",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_TEXT_WHITE,
            height=40,
            corner_radius=9,
            state="disabled",
            command=self._copy_password
        )
        self.copy_btn.grid(row=0, column=1, sticky="ew")

        # Action Button Row 2: "Enregistrer une copie déchiffrée" (Section 13.2)
        self.save_icon = get_icon("save", 16, "#FFFFFF")
        self.save_unlocked_btn = ctk.CTkButton(
            self,
            text="  Enregistrer une copie déchiffrée",
            image=self.save_icon,
            compound="left",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=40,
            corner_radius=9,
            state="disabled",
            command=self.save_unlocked_copy
        )
        self.save_unlocked_btn.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 18))

    def set_result(self, password: str, elapsed_sec: float, attempts: int, pdf_path: str = None):
        """13.1 Positive confirmed result."""
        self.found_password = password
        self.current_pdf_path = pdf_path
        self.decrypted_pdf_path = None

        self.header_icon_lbl.configure(image=self.icon_ok)
        self.result_box.configure(fg_color=COLOR_SUCCESS_BG, border_color=COLOR_SUCCESS_BORDER)
        self.status_subtitle.configure(text="Mot de passe retrouvé !", text_color=COLOR_SUCCESS_TEXT)
        self.pwd_display.configure(text=password, text_color=COLOR_SUCCESS_TEXT)

        doc_name = Path(pdf_path).name if pdf_path else "--"
        self.doc_lbl.configure(text=f"Document : {doc_name}")

        hours = int(elapsed_sec // 3600)
        minutes = int((elapsed_sec % 3600) // 60)
        seconds = int(elapsed_sec % 60)
        self.time_lbl.configure(text=f"Temps écoulé : {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.attempts_lbl.configure(text=f"Essais nécessaires : {attempts:,}".replace(",", " "))
        self.unlocked_badge.configure(text="Cliquez ci-dessous pour enregistrer une copie sans mot de passe.")

        self.open_btn.configure(state="normal")
        self.copy_btn.configure(state="normal")
        self.save_unlocked_btn.configure(
            state="normal",
            text="  Enregistrer une copie déchiffrée",
            fg_color=COLOR_PRIMARY_BLUE
        )

    def set_negative_result(self, title: str, detail: str, elapsed_sec: float = 0.0, attempts: int = 0, pdf_path: str = None):
        """13.3 Negative result or technical error (never displays a fake password!)."""
        self.found_password = None
        self.current_pdf_path = pdf_path
        self.decrypted_pdf_path = None

        self.header_icon_lbl.configure(image=self.icon_err)
        self.result_box.configure(fg_color=COLOR_ERROR_BG, border_color=COLOR_ERROR_BORDER)
        self.status_subtitle.configure(text=title, text_color=COLOR_ERROR_RED)
        self.pwd_display.configure(text="Non trouvé", text_color=COLOR_ERROR_RED)

        doc_name = Path(pdf_path).name if pdf_path else "--"
        self.doc_lbl.configure(text=f"Document : {doc_name}")

        hours = int(elapsed_sec // 3600)
        minutes = int((elapsed_sec % 3600) // 60)
        seconds = int(elapsed_sec % 60)
        self.time_lbl.configure(text=f"Temps écoulé : {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.attempts_lbl.configure(text=f"Essais effectués : {attempts:,}".replace(",", " "))
        self.unlocked_badge.configure(text=detail, text_color=COLOR_ERROR_RED)

        self.open_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.save_unlocked_btn.configure(state="disabled")

    def reset(self):
        self.found_password = None
        self.current_pdf_path = None
        self.decrypted_pdf_path = None

        self.header_icon_lbl.configure(image=self.icon_idle)
        self.result_box.configure(fg_color=COLOR_INPUT_BG, border_color=COLOR_CARD_BORDER)
        self.status_subtitle.configure(text="En attente d'une opération", text_color=COLOR_TEXT_MUTED)
        self.pwd_display.configure(text="------", text_color=COLOR_TEXT_MUTED)
        self.doc_lbl.configure(text="Document : --")
        self.time_lbl.configure(text="Temps écoulé : --:--:--")
        self.attempts_lbl.configure(text="Essais nécessaires : --")
        self.unlocked_badge.configure(text="", text_color=COLOR_SUCCESS_TEXT)

        self.open_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.save_unlocked_btn.configure(
            state="disabled",
            text="  Enregistrer une copie déchiffrée",
            fg_color=COLOR_PRIMARY_BLUE
        )

    def save_unlocked_copy(self, default_output: str = None, prompt_open: bool = True) -> str:
        if not self.found_password or not self.current_pdf_path:
            return None

        p = Path(self.current_pdf_path)
        if not default_output:
            default_name = f"{p.stem}_sans_mot_de_passe{p.suffix}"
            save_path = filedialog.asksaveasfilename(
                title="Enregistrer une copie déchiffrée du PDF",
                initialdir=str(p.parent),
                initialfile=default_name,
                defaultextension=".pdf",
                filetypes=[("Fichier PDF déchiffré (*.pdf)", "*.pdf")]
            )
        else:
            save_path = default_output

        if not save_path:
            return None

        try:
            out_file = CrackerEngine.decrypt_and_save_pdf(self.current_pdf_path, self.found_password, save_path)
            self.decrypted_pdf_path = out_file

            out_name = Path(out_file).name
            self.unlocked_badge.configure(
                text=f"✓ Copie déchiffrée enregistrée : {out_name}",
                text_color=COLOR_SUCCESS_TEXT
            )
            self.save_unlocked_btn.configure(
                text="  Copie déchiffrée enregistrée",
                fg_color=COLOR_SUCCESS_BTN
            )

            if self.on_unlocked_saved:
                self.on_unlocked_saved(out_file)

            if prompt_open:
                answer = messagebox.askyesno(
                    "Copie déchiffrée enregistrée",
                    f"La copie sans mot de passe a été enregistrée et vérifiée :\n\n{out_file}\n\n"
                    "Le document original n'a pas été modifié.\n"
                    "Voulez-vous ouvrir la copie déchiffrée maintenant ?"
                )
                if answer:
                    try:
                        os.startfile(out_file)
                    except Exception as e:
                        messagebox.showerror("Erreur d'ouverture", f"Impossible d'ouvrir le fichier : {e}")

            return out_file

        except Exception as e:
            messagebox.showerror("Erreur d'enregistrement", f"Impossible d'enregistrer la copie déchiffrée :\n{e}")
            return None

    def _copy_password(self):
        if not self.found_password:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(self.found_password)
            self.copy_btn.configure(text="  Mot de passe copié !")
            self.after(2000, lambda: self.copy_btn.configure(text="  Copier le mot de passe"))
        except Exception as e:
            messagebox.showerror("Presse-papier", f"Impossible de copier : {e}")

    def _open_pdf(self):
        target_path = self.decrypted_pdf_path or self.current_pdf_path
        if not target_path or not Path(target_path).exists():
            messagebox.showwarning("Fichier introuvable", "Le fichier PDF sélectionné est introuvable.")
            return
        try:
            os.startfile(target_path)
        except Exception as e:
            messagebox.showerror("Erreur d'ouverture", f"Impossible d'ouvrir le document : {e}")

    def set_compact_labels(self, compact: bool):
        self.copy_btn.configure(text="  Copier le code" if compact else "  Copier le mot de passe")
