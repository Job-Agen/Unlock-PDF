"""
Bottom Status Bar (Footer) for PDF Unlocker Desktop Windows (Section 18 of Master Prompt).
Height: 40 px, Background: #08152A, Top Border: #1B3559.
"""

import customtkinter as ctk
from ui.theme import (
    COLOR_FOOTER_BG, COLOR_CARD_BORDER, COLOR_TEXT_MUTED, COLOR_TEXT_DIM,
    FONT_FAMILY, FOOTER_HEIGHT
)


class Footer(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_FOOTER_BG,
            corner_radius=0,
            height=FOOTER_HEIGHT,
            **kwargs
        )
        self.grid_propagate(False)
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top 1px border (#1B3559)
        top_border = ctk.CTkFrame(self, fg_color=COLOR_CARD_BORDER, height=1, corner_radius=0)
        top_border.grid(row=0, column=0, sticky="ew")

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=1, column=0, sticky="nsew", padx=24)
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(1, weight=1)

        left_box = ctk.CTkFrame(inner, fg_color="transparent")
        left_box.grid(row=0, column=0, sticky="w")

        dot_lbl = ctk.CTkLabel(
            left_box,
            text="●",
            font=(FONT_FAMILY, 11),
            text_color="#16D18C"
        )
        dot_lbl.grid(row=0, column=0, padx=(0, 8))

        self.version_lbl = ctk.CTkLabel(
            left_box,
            text="PDF Unlocker v1.0.0   •   Traitement 100 % local sur Windows",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED
        )
        self.version_lbl.grid(row=0, column=1, sticky="w")

        self.right_lbl = ctk.CTkLabel(
            inner,
            text="À usage personnel uniquement   •   Vos fichiers restent sur votre ordinateur",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_DIM
        )
        self.right_lbl.grid(row=0, column=2, sticky="e")

    def set_compact_mode(self, compact: bool):
        if compact:
            self.right_lbl.configure(text="À usage personnel uniquement")
        else:
            self.right_lbl.configure(text="À usage personnel uniquement   •   Vos fichiers restent sur votre ordinateur")
