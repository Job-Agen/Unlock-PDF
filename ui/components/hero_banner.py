"""
Hero Banner component for PDF Unlocker Desktop Windows (Section 7.2 of Master Prompt).
Left: 3D red PDF document illustration with padlock.
Right: 'Déverrouillez votre PDF' (27 px bold #F3F7FF) and adaptive multi-line description (#C5DAFB).
"""

import customtkinter as ctk
from ui.theme import (
    COLOR_HERO_BG, COLOR_HERO_BORDER, COLOR_TEXT_WHITE, COLOR_HERO_TEXT,
    FONT_FAMILY, FONT_SIZE_HERO_TITLE, RADIUS_CARD_PRIMARY
)
from ui.icons import create_pdf_hero_image


class HeroBanner(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_HERO_BG,
            corner_radius=RADIUS_CARD_PRIMARY,
            border_width=1,
            border_color=COLOR_HERO_BORDER,
            **kwargs
        )
        self._build_ui()
        self.bind("<Configure>", self._on_resize)

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Left: 3D Red PDF Document + Padlock illustration (Section 7.2)
        self.hero_img_normal = create_pdf_hero_image(104, 112)
        self.hero_img_compact = create_pdf_hero_image(70, 76)
        self.img_label = ctk.CTkLabel(self, image=self.hero_img_normal, text="")
        self.img_label.grid(row=0, column=0, padx=(24, 20), pady=20, sticky="w")

        # Right: Title and Description centered vertically
        self.text_box = ctk.CTkFrame(self, fg_color="transparent")
        self.text_box.grid(row=0, column=1, padx=(0, 24), pady=20, sticky="ew")
        self.text_box.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self.text_box,
            text="Déverrouillez votre PDF",
            font=(FONT_FAMILY, FONT_SIZE_HERO_TITLE, "bold"),
            text_color=COLOR_TEXT_WHITE,
            anchor="w",
            justify="left"
        )
        self.title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.desc_lbl = ctk.CTkLabel(
            self.text_box,
            text="Entrez les informations ci-dessous et lancez la recherche du mot de passe. "
                 "Notre outil va tester toutes les combinaisons configurées et vous aider à retrouver l'accès à votre document.",
            font=(FONT_FAMILY, 14),
            text_color=COLOR_HERO_TEXT,
            justify="left",
            anchor="w",
            wraplength=540
        )
        self.desc_lbl.grid(row=1, column=0, sticky="ew")

    def _on_resize(self, event=None):
        if event and event.width > 240:
            avail = max(260, event.width - 185)
            self.desc_lbl.configure(wraplength=avail)

    def set_compact_vertical(self, compact: bool):
        py = 10 if compact else 20
        self.img_label.configure(image=self.hero_img_compact if compact else self.hero_img_normal)
        self.img_label.grid_configure(pady=py, padx=(16, 14) if compact else (24, 20))
        self.text_box.grid_configure(pady=py)
        self.title_lbl.configure(font=(FONT_FAMILY, 21 if compact else FONT_SIZE_HERO_TITLE, "bold"))
        self.title_lbl.grid_configure(pady=(0, 3 if compact else 8))
        self.desc_lbl.configure(font=(FONT_FAMILY, 12 if compact else 14))
