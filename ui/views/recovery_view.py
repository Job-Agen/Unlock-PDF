"""
Specialized Recovery Methods View (Page Récupération — Section 14 of Master Prompt & Reference Image 3).
Displays the 4 selectable recovery method cards in a 2x2 grid:
1. Codes numériques
2. Mots de passe personnalisés / probables
3. Liste de mots de passe
4. Attaque par masque (?)
Along with the dynamic 'Paramètres avancés' configuration card and 'Lancer la récupération' button.
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from ui.theme import (
    COLOR_BG_ROOT, COLOR_CARD_BG, COLOR_CARD_SECONDARY, COLOR_CARD_BORDER,
    COLOR_PRIMARY_BLUE, COLOR_PRIMARY_HOVER, COLOR_CYAN,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_INPUT_BG,
    FONT_FAMILY, FONT_MONO, MAIN_MARGIN_X, MAIN_MARGIN_Y
)
from ui.icons import get_icon


class RecoveryView(ctk.CTkFrame):
    METHOD_SPECS = [
        {
            "id": "Codes numériques (0-9)",
            "title": "Codes numériques",
            "desc": "Tester tous les codes de 4 à 8 chiffres.",
            "example": "Ex : 123456, 000452...",
            "icon": "num_pad",
        },
        {
            "id": "Mot de passe candidat",
            "title": "Mots de passe personnalisés",
            "desc": "Vérifier un mot de passe ou code connu.",
            "example": "Ex : date, nom, code à 6 chiffres...",
            "icon": "key_star",
        },
        {
            "id": "Liste de mots de passe",
            "title": "Liste de mots de passe",
            "desc": "Tester une liste personnalisée de candidats.",
            "example": "Ex : mots courants, variantes, fichier .txt...",
            "icon": "file_doc",
        },
        {
            "id": "Mot de passe partiellement connu (?)",
            "title": "Attaque par masque",
            "desc": "Définir un modèle de mot de passe partiellement connu.",
            "example": "Ex : 4827??, 2024??...",
            "icon": "mask_code",
        },
    ]

    def __init__(self, master, on_launch_method=None, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_ROOT, corner_radius=0, **kwargs)
        self.on_launch_method = on_launch_method
        self.selected_method_id = self.METHOD_SPECS[0]["id"]
        self.method_cards = {}
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=MAIN_MARGIN_X, pady=MAIN_MARGIN_Y)
        container.grid_columnconfigure(0, weight=1)

        # Page Title & Subtitle
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        ctk.CTkLabel(
            header,
            text="Méthodes de récupération",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Choisissez une méthode adaptée à votre situation.",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(4, 0))

        # 2x2 Grid of Method Cards (Section 14)
        grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        grid_frame.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        grid_frame.grid_columnconfigure(0, weight=1, uniform="rec_cards")
        grid_frame.grid_columnconfigure(1, weight=1, uniform="rec_cards")

        for idx, spec in enumerate(self.METHOD_SPECS):
            r = idx // 2
            c = idx % 2
            card = self._create_method_card(grid_frame, spec)
            card.grid(
                row=r,
                column=c,
                sticky="nsew",
                padx=(0, 10) if c == 0 else (10, 0),
                pady=(0, 16)
            )
            self.method_cards[spec["id"]] = card

        # Advanced Parameters Card (Section 14)
        self.adv_card = ctk.CTkFrame(
            container,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        self.adv_card.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        self.adv_card.grid_columnconfigure(0, weight=1)

        adv_head = ctk.CTkFrame(self.adv_card, fg_color="transparent")
        adv_head.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 14))

        gear_ic = get_icon("gear", 18, COLOR_CYAN)
        ctk.CTkLabel(adv_head, image=gear_ic, text="").grid(row=0, column=0, padx=(0, 10))
        ctk.CTkLabel(
            adv_head,
            text="Paramètres avancés",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).grid(row=0, column=1, sticky="w")

        # Dynamic fields container inside Advanced Parameters
        self.dynamic_box = ctk.CTkFrame(self.adv_card, fg_color="transparent")
        self.dynamic_box.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 14))
        self.dynamic_box.grid_columnconfigure(0, weight=1)
        self.dynamic_box.grid_columnconfigure(1, weight=2)

        # Numeric range widgets
        self.len_box = ctk.CTkFrame(self.dynamic_box, fg_color="transparent")
        self.len_box.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        self.len_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.len_box, text="Longueur", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.len_menu = ctk.CTkOptionMenu(
            self.len_box,
            values=["4 chiffres", "5 chiffres", "6 chiffres", "7 chiffres", "8 chiffres"],
            command=self._on_len_change,
            fg_color=COLOR_INPUT_BG,
            button_color="#162947",
            button_hover_color="#1F3860",
            text_color=COLOR_TEXT_WHITE,
            height=40,
            corner_radius=8
        )
        self.len_menu.set("6 chiffres")
        self.len_menu.grid(row=1, column=0, sticky="ew")

        self.rng_box = ctk.CTkFrame(self.dynamic_box, fg_color="transparent")
        self.rng_box.grid(row=0, column=1, sticky="ew")
        self.rng_box.grid_columnconfigure(0, weight=1)
        self.rng_box.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(self.rng_box, text="Plage de recherche", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))
        self.start_entry = ctk.CTkEntry(self.rng_box, fg_color=COLOR_INPUT_BG, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_WHITE, font=(FONT_MONO, 13), height=40)
        self.start_entry.insert(0, "000000")
        self.start_entry.grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(self.rng_box, text="  à  ", font=(FONT_FAMILY, 13), text_color=COLOR_TEXT_MUTED).grid(row=1, column=1)
        self.end_entry = ctk.CTkEntry(self.rng_box, fg_color=COLOR_INPUT_BG, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_WHITE, font=(FONT_MONO, 13), height=40)
        self.end_entry.insert(0, "999999")
        self.end_entry.grid(row=1, column=2, sticky="ew")

        # Text / Pattern input for non-numeric methods
        self.pattern_box = ctk.CTkFrame(self.dynamic_box, fg_color="transparent")
        self.pattern_box.grid_columnconfigure(0, weight=1)
        self.pattern_lbl = ctk.CTkLabel(self.pattern_box, text="Valeur ou motif :", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED)
        self.pattern_lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.pattern_entry = ctk.CTkEntry(self.pattern_box, fg_color=COLOR_INPUT_BG, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_WHITE, font=(FONT_MONO, 13), height=40)
        self.pattern_entry.grid(row=1, column=0, sticky="ew")
        self.browse_txt_btn = ctk.CTkButton(
            self.pattern_box,
            text="Parcourir .txt",
            fg_color="#1B2D4E",
            hover_color="#253D65",
            height=40,
            width=120,
            command=self._pick_txt
        )

        # Checkboxes row matching Reference Image 3
        chk_grid = ctk.CTkFrame(self.adv_card, fg_color="transparent")
        chk_grid.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 18))

        self.chk_opt = ctk.CTkCheckBox(chk_grid, text="Optimiser la recherche (plus rapide)", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_WHITE, fg_color=COLOR_PRIMARY_BLUE)
        self.chk_opt.select()
        self.chk_opt.grid(row=0, column=0, padx=(0, 24), pady=4, sticky="w")

        self.chk_save = ctk.CTkCheckBox(chk_grid, text="Sauvegarder la progression", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_WHITE, fg_color=COLOR_PRIMARY_BLUE)
        self.chk_save.select()
        self.chk_save.grid(row=0, column=1, pady=4, sticky="w")

        self.chk_stop_first = ctk.CTkCheckBox(chk_grid, text="Arrêter après la première correspondance", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_WHITE, fg_color=COLOR_PRIMARY_BLUE)
        self.chk_stop_first.select()
        self.chk_stop_first.grid(row=1, column=0, columnspan=2, pady=(6, 0), sticky="w")

        # Launch Button
        play_ic = get_icon("play", 16, "#FFFFFF")
        self.launch_btn = ctk.CTkButton(
            self.adv_card,
            text="  Lancer la récupération",
            image=play_ic,
            compound="left",
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=48,
            corner_radius=10,
            command=self._handle_launch
        )
        self.launch_btn.grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 22))

        self._refresh_selection_visuals()

    def _create_method_card(self, parent, spec: dict) -> ctk.CTkFrame:
        m_id = spec["id"]
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        card.grid_columnconfigure(1, weight=1)

        icon_box = ctk.CTkFrame(card, fg_color="#122B54", width=46, height=46, corner_radius=12)
        icon_box.grid(row=0, column=0, rowspan=3, padx=(18, 14), pady=18, sticky="nw")
        icon_box.grid_propagate(False)

        ic = get_icon(spec["icon"], 22, COLOR_CYAN)
        ic_lbl = ctk.CTkLabel(icon_box, image=ic, text="")
        ic_lbl.place(relx=0.5, rely=0.5, anchor="center")

        title_lbl = ctk.CTkLabel(
            card,
            text=spec["title"],
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE,
            anchor="w"
        )
        title_lbl.grid(row=0, column=1, sticky="w", padx=(0, 16), pady=(18, 2))

        desc_lbl = ctk.CTkLabel(
            card,
            text=spec["desc"],
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
            justify="left"
        )
        desc_lbl.grid(row=1, column=1, sticky="w", padx=(0, 16))

        ex_lbl = ctk.CTkLabel(
            card,
            text=spec["example"],
            font=(FONT_FAMILY, 11),
            text_color="#6F91BD",
            anchor="w"
        )
        ex_lbl.grid(row=2, column=1, sticky="w", padx=(0, 16), pady=(4, 18))

        for widget in (card, icon_box, ic_lbl, title_lbl, desc_lbl, ex_lbl):
            widget.bind("<Button-1>", lambda e, mid=m_id: self.select_method(mid))

        return card

    def select_method(self, method_id: str):
        self.selected_method_id = method_id
        self._refresh_selection_visuals()

    def _refresh_selection_visuals(self):
        for mid, card in self.method_cards.items():
            if mid == self.selected_method_id:
                card.configure(
                    fg_color=COLOR_CARD_SECONDARY,
                    border_color=COLOR_PRIMARY_BLUE,
                    border_width=2
                )
            else:
                card.configure(
                    fg_color=COLOR_CARD_BG,
                    border_color=COLOR_CARD_BORDER,
                    border_width=1
                )

        if self.selected_method_id == "Codes numériques (0-9)":
            self.pattern_box.grid_remove()
            self.len_box.grid(row=0, column=0, sticky="ew", padx=(0, 16))
            self.rng_box.grid(row=0, column=1, sticky="ew")
        else:
            self.len_box.grid_remove()
            self.rng_box.grid_remove()
            self.pattern_box.grid(row=0, column=0, columnspan=2, sticky="ew")
            self.pattern_entry.delete(0, "end")

            if self.selected_method_id == "Mot de passe candidat":
                self.pattern_lbl.configure(text="Mot de passe candidat à vérifier :")
                self.pattern_entry.insert(0, "000452")
                self.browse_txt_btn.grid_remove()
            elif self.selected_method_id == "Liste de mots de passe":
                self.pattern_lbl.configure(text="Liste de mots de passe candidats (séparés par virgule) :")
                self.pattern_entry.insert(0, "123456, 000452, 202400")
                self.browse_txt_btn.grid(row=1, column=1, padx=(10, 0))
            else:
                self.pattern_lbl.configure(text="Modèle de masque avec '?' (chaque '?' = 1 chiffre inconnu) :")
                self.pattern_entry.insert(0, "4827??")
                self.browse_txt_btn.grid_remove()

    def _on_len_change(self, choice: str):
        mapping = {
            "4 chiffres": ("0000", "9999"),
            "5 chiffres": ("00000", "99999"),
            "6 chiffres": ("000000", "999999"),
            "7 chiffres": ("0000000", "9999999"),
            "8 chiffres": ("00000000", "99999999"),
        }
        if choice in mapping:
            s, e = mapping[choice]
            self.start_entry.delete(0, "end")
            self.start_entry.insert(0, s)
            self.end_entry.delete(0, "end")
            self.end_entry.insert(0, e)

    def _pick_txt(self):
        f = filedialog.askopenfilename(
            title="Importer une liste (.txt)",
            filetypes=[("Fichiers texte (*.txt)", "*.txt")]
        )
        if f:
            try:
                raw = Path(f).read_text(encoding="utf-8", errors="ignore").strip()
                items = [line.strip() for line in raw.splitlines() if line.strip()]
                self.pattern_entry.delete(0, "end")
                self.pattern_entry.insert(0, ", ".join(items))
            except Exception:
                pass

    def _handle_launch(self):
        preset = self.pattern_entry.get().strip() if self.selected_method_id != "Codes numériques (0-9)" else ""
        if self.on_launch_method:
            self.on_launch_method(self.selected_method_id, preset)

