"""
TopBar component for PDF Unlocker Desktop Windows (Section 5 of Master Prompt).
Height: 84 px, Background: #0B1930, Bottom Border: #1B3559.
Displays the 48x48 vector lock logo, application title, subtitle, status badge, and settings button.
"""

import customtkinter as ctk
from ui.theme import (
    COLOR_TOPBAR_BG, COLOR_CARD_BORDER, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_NAV_HOVER_BG, FONT_FAMILY, FONT_SIZE_APP_TITLE, TOPBAR_HEIGHT
)
from ui.icons import create_app_logo_image, get_icon


class TopBar(ctk.CTkFrame):
    def __init__(self, master, on_open_settings=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_TOPBAR_BG,
            corner_radius=0,
            height=TOPBAR_HEIGHT,
            **kwargs
        )
        self.on_open_settings = on_open_settings
        self.grid_propagate(False)
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=0, sticky="nsew", padx=24)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        # Left: 48x48 Logo + Title & Subtitle
        left_box = ctk.CTkFrame(content, fg_color="transparent")
        left_box.grid(row=0, column=0, sticky="w")

        self.logo_img = create_app_logo_image(48)
        logo_lbl = ctk.CTkLabel(left_box, image=self.logo_img, text="")
        logo_lbl.grid(row=0, column=0, rowspan=2, padx=(0, 14), pady=2)

        self.title_lbl = ctk.CTkLabel(
            left_box,
            text="PDF Unlocker",
            font=(FONT_FAMILY, FONT_SIZE_APP_TITLE, "bold"),
            text_color=COLOR_TEXT_WHITE,
            anchor="w"
        )
        self.title_lbl.grid(row=0, column=1, sticky="sw", pady=(2, 0))

        self.subtitle_lbl = ctk.CTkLabel(
            left_box,
            text="Récupérez le mot de passe de vos fichiers PDF",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.subtitle_lbl.grid(row=1, column=1, sticky="nw", pady=(0, 2))

        # Right: Status pill + Settings gear icon button (matching reference image)
        right_box = ctk.CTkFrame(content, fg_color="transparent")
        right_box.grid(row=0, column=2, sticky="e")

        self.status_pill = ctk.CTkFrame(
            right_box,
            fg_color="#081427",
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        self.status_pill.grid(row=0, column=0, padx=(0, 12))

        dot = ctk.CTkLabel(
            self.status_pill,
            text="●",
            font=(FONT_FAMILY, 11),
            text_color="#16D18C"
        )
        dot.grid(row=0, column=0, padx=(10, 5), pady=5)

        self.status_text = ctk.CTkLabel(
            self.status_pill,
            text="Moteur local prêt",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED
        )
        self.status_text.grid(row=0, column=1, padx=(0, 12), pady=5)

        self.settings_icon = get_icon("settings", 20, COLOR_TEXT_MUTED)
        self.settings_btn = ctk.CTkButton(
            right_box,
            text="",
            image=self.settings_icon,
            width=40,
            height=40,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLOR_NAV_HOVER_BG,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            command=self._handle_settings_click
        )
        self.settings_btn.grid(row=0, column=1)

        # Bottom 1px border line
        border_line = ctk.CTkFrame(self, fg_color=COLOR_CARD_BORDER, height=1, corner_radius=0)
        border_line.grid(row=1, column=0, sticky="ew")

    def _handle_settings_click(self):
        if self.on_open_settings:
            self.on_open_settings()

    def set_compact_mode(self, compact: bool):
        """Hides secondary status pill on narrow windows before touching the title (Section 5.4)."""
        if compact:
            self.status_pill.grid_remove()
        else:
            self.status_pill.grid(row=0, column=0, padx=(0, 12))

