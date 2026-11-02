"""
History View (Page Historique — Section 16 of Master Prompt).
Displays past operations with filters, structured table columns (Fichier, Date, Durée, Statut, Actions),
protects sensitive data (never stores plaintext passwords), and displays an elegant empty state.
"""

import customtkinter as ctk
from tkinter import messagebox
from ui.theme import (
    COLOR_BG_ROOT, COLOR_CARD_BG, COLOR_CARD_BORDER,
    COLOR_SECONDARY_BTN, COLOR_SECONDARY_HOVER, COLOR_SUCCESS_TEXT,
    COLOR_ERROR_RED, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_DIM,
    COLOR_INPUT_BG, FONT_FAMILY, FONT_MONO, MAIN_MARGIN_X, MAIN_MARGIN_Y
)
from ui.icons import get_icon
from core.history_manager import HistoryManager


class HistoryView(ctk.CTkFrame):
    def __init__(self, master, history: HistoryManager, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_ROOT, corner_radius=0, **kwargs)
        self.history = history
        self.current_filter = "Tous les statuts"
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header + Filter Bar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=MAIN_MARGIN_X, pady=(MAIN_MARGIN_Y, 16))
        header.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_box,
            text="Historique",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Consultez le journal des opérations passées (aucun mot de passe en clair n'est stocké sur disque).",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(3, 0))

        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.grid(row=0, column=1, sticky="e")

        self.filter_menu = ctk.CTkOptionMenu(
            controls,
            values=["Tous les statuts", "Déverrouillé", "Échec", "Interruption"],
            command=self._on_filter_changed,
            fg_color=COLOR_INPUT_BG,
            button_color="#162947",
            button_hover_color="#1F3860",
            text_color=COLOR_TEXT_WHITE,
            height=36,
            width=165,
            corner_radius=8
        )
        self.filter_menu.set("Tous les statuts")
        self.filter_menu.pack(side="left", padx=(0, 10))

        trash_ic = get_icon("trash", 15, COLOR_ERROR_RED)
        clear_btn = ctk.CTkButton(
            controls,
            text="  Effacer l'historique",
            image=trash_ic,
            compound="left",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_ERROR_RED,
            height=36,
            corner_radius=8,
            command=self._clear_history
        )
        clear_btn.pack(side="left")

        # Table Card
        table_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        table_card.grid(row=1, column=0, sticky="nsew", padx=MAIN_MARGIN_X, pady=(0, MAIN_MARGIN_Y))
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        thead = ctk.CTkFrame(table_card, fg_color="#081427", corner_radius=8, height=40)
        thead.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 6))
        thead.grid_propagate(False)
        thead.grid_columnconfigure(0, weight=4, uniform="hcols")
        thead.grid_columnconfigure(1, weight=3, uniform="hcols")
        thead.grid_columnconfigure(2, weight=2, uniform="hcols")
        thead.grid_columnconfigure(3, weight=2, uniform="hcols")
        thead.grid_columnconfigure(4, weight=2, uniform="hcols")

        for idx, col_title in enumerate(["Fichier", "Date", "Durée", "Statut", "Essais"]):
            ctk.CTkLabel(
                thead,
                text=col_title,
                font=(FONT_FAMILY, 12, "bold"),
                text_color=COLOR_TEXT_MUTED,
                anchor="w"
            ).grid(row=0, column=idx, sticky="ew", padx=14, pady=8)

        self.list_container = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.list_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 14))
        self.list_container.grid_columnconfigure(0, weight=1)

        self.refresh_list()

    def _on_filter_changed(self, value: str):
        self.current_filter = value
        self.refresh_list()

    def refresh_list(self):
        for w in self.list_container.winfo_children():
            w.destroy()

        items = self.history.get_all()
        if self.current_filter != "Tous les statuts":
            items = [it for it in items if it.get("status") == self.current_filter]

        if not items:
            empty_frame = ctk.CTkFrame(self.list_container, fg_color="transparent")
            empty_frame.grid(row=0, column=0, sticky="ew", pady=56)
            ctk.CTkLabel(
                empty_frame,
                text="Aucune opération enregistrée dans l'historique.",
                font=(FONT_FAMILY, 14, "bold"),
                text_color=COLOR_TEXT_MUTED
            ).pack()
            ctk.CTkLabel(
                empty_frame,
                text="Par mesure de confidentialité, l'historique local est désactivé par défaut dans les Paramètres.",
                font=(FONT_FAMILY, 12),
                text_color=COLOR_TEXT_DIM
            ).pack(pady=(4, 0))
            return

        for idx, item in enumerate(items):
            bg = "#0E213E" if idx % 2 == 1 else "transparent"
            row = ctk.CTkFrame(self.list_container, fg_color=bg, corner_radius=8, height=44)
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=4, uniform="hcols")
            row.grid_columnconfigure(1, weight=3, uniform="hcols")
            row.grid_columnconfigure(2, weight=2, uniform="hcols")
            row.grid_columnconfigure(3, weight=2, uniform="hcols")
            row.grid_columnconfigure(4, weight=2, uniform="hcols")

            fname = item.get("filename", "document.pdf")
            ctk.CTkLabel(row, text=fname, font=(FONT_FAMILY, 13, "bold"), text_color=COLOR_TEXT_WHITE, anchor="w").grid(row=0, column=0, sticky="ew", padx=14, pady=8)
            ctk.CTkLabel(row, text=item.get("date", "--"), font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED, anchor="w").grid(row=0, column=1, sticky="ew", padx=14, pady=8)
            ctk.CTkLabel(row, text=item.get("duration", "--"), font=(FONT_MONO, 12), text_color=COLOR_TEXT_MUTED, anchor="w").grid(row=0, column=2, sticky="ew", padx=14, pady=8)

            st = item.get("status", "Déverrouillé")
            st_col = COLOR_SUCCESS_TEXT if st == "Déverrouillé" else COLOR_ERROR_RED
            ctk.CTkLabel(row, text=st, font=(FONT_FAMILY, 12, "bold"), text_color=st_col, anchor="w").grid(row=0, column=3, sticky="ew", padx=14, pady=8)

            att = f"{item.get('attempts', 0):,}".replace(",", " ")
            ctk.CTkLabel(row, text=att, font=(FONT_MONO, 12), text_color=COLOR_TEXT_MUTED, anchor="w").grid(row=0, column=4, sticky="ew", padx=14, pady=8)

    def _clear_history(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment effacer tout l'historique local ?"):
            self.history.clear()
            self.refresh_list()
