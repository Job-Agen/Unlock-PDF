"""
Sidebar navigation component for PDF Unlocker Desktop Windows (Section 6 of Master Prompt).
Width: 268 px, Background: #08162C, 7 vector-icon navigation items, and bottom Premium card.
"""

import customtkinter as ctk
from ui.theme import (
    COLOR_SIDEBAR_BG, COLOR_CARD_BORDER, COLOR_PRIMARY_BLUE, COLOR_PRIMARY_HOVER,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_NAV_ACTIVE_BG, COLOR_NAV_HOVER_BG,
    COLOR_NAV_INACTIVE_TEXT, COLOR_PROMO_BG, COLOR_PROMO_BORDER,
    FONT_FAMILY, RADIUS_NAV_ITEM, SIDEBAR_WIDTH, SIDEBAR_COMPACT_WIDTH
)
from ui.icons import get_icon


class Sidebar(ctk.CTkFrame):
    NAV_ITEMS = [
        ("Accueil", "home", "Accueil"),
        ("Déverrouiller", "unlock", "Déverrouiller"),
        ("Récupération", "recovery", "Récupération"),
        ("Traitement par lots", "batch", "Traitement par lots"),
        ("Historique", "history", "Historique"),
        ("Paramètres", "settings", "Paramètres"),
        ("Aide", "help", "Aide"),
    ]

    def __init__(self, master, on_tab_selected, on_discover_premium=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_SIDEBAR_BG,
            corner_radius=0,
            width=SIDEBAR_WIDTH,
            **kwargs
        )
        self.on_tab_selected = on_tab_selected
        self.on_discover_premium = on_discover_premium
        self.active_tab = "Accueil"
        self.buttons = {}
        self.icons_active = {}
        self.icons_inactive = {}

        self.grid_propagate(False)
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=0)  # Nav list
        self.grid_rowconfigure(1, weight=1)  # Flexible spacer
        self.grid_rowconfigure(2, weight=0)  # Premium card
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)  # Right border line

        # 1. Navigation items container
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.grid(row=0, column=0, sticky="ew", padx=18, pady=(20, 8))
        self.nav_frame.grid_columnconfigure(0, weight=1)

        for idx, (key, icon_name, label) in enumerate(self.NAV_ITEMS):
            ic_active = get_icon(icon_name, 19, COLOR_TEXT_WHITE)
            ic_inactive = get_icon(icon_name, 19, COLOR_TEXT_MUTED)
            self.icons_active[key] = ic_active
            self.icons_inactive[key] = ic_inactive

            is_act = key == self.active_tab
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"  {label}",
                image=ic_active if is_act else ic_inactive,
                compound="left",
                font=(FONT_FAMILY, 13, "bold" if is_act else "normal"),
                fg_color=COLOR_NAV_ACTIVE_BG if is_act else "transparent",
                hover_color=COLOR_NAV_ACTIVE_BG if is_act else COLOR_NAV_HOVER_BG,
                text_color=COLOR_TEXT_WHITE if is_act else COLOR_NAV_INACTIVE_TEXT,
                anchor="w",
                corner_radius=RADIUS_NAV_ITEM,
                height=46,
                command=lambda k=key: self.select_tab(k)
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=3)
            self.buttons[key] = btn

        # 2. Spacer
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.grid(row=1, column=0, sticky="nsew")

        # 3. Encadré Premium (Section 6.4)
        self.promo_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_PROMO_BG,
            corner_radius=14,
            border_width=1,
            border_color=COLOR_PROMO_BORDER
        )
        self.promo_card.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 20))
        self.promo_card.grid_columnconfigure(0, weight=1)

        top_promo = ctk.CTkFrame(self.promo_card, fg_color="transparent")
        top_promo.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))

        crown_badge = ctk.CTkFrame(
            top_promo,
            fg_color="#123163",
            width=32,
            height=32,
            corner_radius=9
        )
        crown_badge.grid(row=0, column=0, padx=(0, 10))
        crown_badge.grid_propagate(False)

        self.crown_icon = get_icon("crown", 18, "#F6B94A")
        self.check_pro_icon = get_icon("check_circle", 18, "#16D18C")
        self.crown_lbl = ctk.CTkLabel(crown_badge, image=self.crown_icon, text="")
        self.crown_lbl.place(relx=0.5, rely=0.5, anchor="center")

        self.promo_title = ctk.CTkLabel(
            top_promo,
            text="Version Premium",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXT_WHITE,
            anchor="w"
        )
        self.promo_title.grid(row=0, column=1, sticky="w")

        self.promo_desc = ctk.CTkLabel(
            self.promo_card,
            text="Débloquez toutes les\nfonctionnalités avancées.",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        self.promo_desc.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        self.promo_btn = ctk.CTkButton(
            self.promo_card,
            text="Découvrir Premium",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=36,
            corner_radius=9,
            command=self._handle_premium_click
        )
        self.promo_btn.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))

        # Right 1px border line
        border_right = ctk.CTkFrame(self, fg_color=COLOR_CARD_BORDER, width=1, corner_radius=0)
        border_right.grid(row=0, column=1, rowspan=3, sticky="ns")

    def _handle_premium_click(self):
        if self.on_discover_premium:
            self.on_discover_premium()
        else:
            self.select_tab("Paramètres")

    def select_tab(self, tab_name: str, notify: bool = True):
        if tab_name not in self.buttons:
            return
        self.active_tab = tab_name
        for key, btn in self.buttons.items():
            if key == tab_name:
                btn.configure(
                    fg_color=COLOR_NAV_ACTIVE_BG,
                    hover_color=COLOR_NAV_ACTIVE_BG,
                    text_color=COLOR_TEXT_WHITE,
                    image=self.icons_active[key],
                    font=(FONT_FAMILY, 13, "bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=COLOR_NAV_HOVER_BG,
                    text_color=COLOR_NAV_INACTIVE_TEXT,
                    image=self.icons_inactive[key],
                    font=(FONT_FAMILY, 13, "normal")
                )
        if notify and self.on_tab_selected:
            self.on_tab_selected(tab_name)

    def apply_responsive_dimensions(self, window_width: int, window_height: int):
        """Adapts sidebar width and promo card visibility according to Sections 6.4 & 19.4."""
        target_w = SIDEBAR_COMPACT_WIDTH if window_width < 1260 else SIDEBAR_WIDTH
        if self.cget("width") != target_w:
            self.configure(width=target_w)

        # If window height is tight (< 800 px), compact the promo description so it never overlaps nav
        if window_height < 800:
            self.promo_desc.grid_remove()
        else:
            self.promo_desc.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

    def update_license_badge(self, is_pro: bool, tier: str = "Pro"):
        """Updates the bottom sidebar card based on Free vs Pro/Business activation state."""
        if is_pro:
            self.promo_card.configure(fg_color="#062229", border_color="#087C5A")
            self.crown_lbl.configure(image=self.check_pro_icon)
            self.promo_title.configure(text=f"Version {tier}", text_color="#16D18C")
            self.promo_desc.configure(text="Activée — Toutes les\nfonctionnalités sont disponibles.")
            self.promo_btn.configure(
                text="Gérer la licence",
                fg_color="#1B2D4E",
                hover_color="#253D65"
            )
        else:
            self.promo_card.configure(fg_color=COLOR_PROMO_BG, border_color=COLOR_PROMO_BORDER)
            self.crown_lbl.configure(image=self.crown_icon)
            self.promo_title.configure(text="Version Premium", text_color=COLOR_TEXT_WHITE)
            self.promo_desc.configure(text="Débloquez toutes les\nfonctionnalités avancées.")
            self.promo_btn.configure(
                text="Découvrir Premium",
                fg_color=COLOR_PRIMARY_BLUE,
                hover_color=COLOR_PRIMARY_HOVER
            )
