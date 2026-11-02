"""
Recovery Parameters Card component for PDF Unlocker Desktop Windows (Section 9 of Master Prompt).
Supports:
- Méthode de récupération (Codes numériques, Mot de passe candidat, Liste de candidats, Motif partiellement connu '?')
- Longueur du mot de passe (4 à 8 chiffres)
- Plage de recherche (avec conservation des zéros initiaux ex: 000000 à 999999)
- Cases à cocher réelles (Optimiser multithread, Arrêter à la première correspondance).
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from ui.theme import (
    COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_INPUT_BG, COLOR_PRIMARY_BLUE, COLOR_SECONDARY_BTN, COLOR_SECONDARY_HOVER,
    COLOR_CYAN, COLOR_ERROR_RED, FONT_FAMILY, FONT_MONO, RADIUS_INPUT
)
from ui.icons import get_icon
from core.engine import CrackerEngine


class SearchParams(ctk.CTkFrame):
    METHODS = [
        "Codes numériques",
        "Mot de passe candidat",
        "Liste de mots de passe",
        "Motif partiel (?)"
    ]

    def __init__(self, master, on_params_changed=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            **kwargs
        )
        self.on_params_changed = on_params_changed
        self.current_method = self.METHODS[0]
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # 9.1 Header (Icône engrenage + Titre "Paramètres de récupération")
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 12))

        self.gear_icon = get_icon("gear", 18, COLOR_CYAN)
        icon_lbl = ctk.CTkLabel(self.header_frame, image=self.gear_icon, text="")
        icon_lbl.grid(row=0, column=0, padx=(0, 10))

        title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="Paramètres de récupération",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE
        )
        title_lbl.grid(row=0, column=1, sticky="w")

        # 9.2 - 9.4 Top Controls Grid (Type de recherche | Longueur | Plage)
        self.top_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.top_grid.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 10))
        self.top_grid.grid_columnconfigure(0, weight=4)
        self.top_grid.grid_columnconfigure(1, weight=3)
        self.top_grid.grid_columnconfigure(2, weight=5)

        # Col 0: Type / Méthode de récupération
        method_col = ctk.CTkFrame(self.top_grid, fg_color="transparent")
        method_col.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        method_col.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            method_col,
            text="Type de recherche",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.method_menu = ctk.CTkOptionMenu(
            method_col,
            values=self.METHODS,
            command=self._on_method_selected,
            font=(FONT_FAMILY, 13),
            fg_color=COLOR_INPUT_BG,
            button_color="#162947",
            button_hover_color="#1F3860",
            text_color=COLOR_TEXT_WHITE,
            dropdown_fg_color="#0B1930",
            dropdown_text_color=COLOR_TEXT_WHITE,
            dropdown_hover_color="#103A82",
            height=40,
            corner_radius=RADIUS_INPUT
        )
        self.method_menu.set(self.METHODS[0])
        self.method_menu.grid(row=1, column=0, sticky="ew")

        # Col 1: Longueur du mot de passe (visible en mode numérique)
        self.len_col = ctk.CTkFrame(self.top_grid, fg_color="transparent")
        self.len_col.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.len_col.grid_columnconfigure(0, weight=1)

        self.len_title_lbl = ctk.CTkLabel(
            self.len_col,
            text="Longueur du mot de passe",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.len_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.length_menu = ctk.CTkOptionMenu(
            self.len_col,
            values=["4 chiffres", "5 chiffres", "6 chiffres", "7 chiffres", "8 chiffres"],
            command=self._on_length_selected,
            font=(FONT_FAMILY, 13),
            fg_color=COLOR_INPUT_BG,
            button_color="#162947",
            button_hover_color="#1F3860",
            text_color=COLOR_TEXT_WHITE,
            dropdown_fg_color="#0B1930",
            dropdown_text_color=COLOR_TEXT_WHITE,
            dropdown_hover_color="#103A82",
            height=40,
            corner_radius=RADIUS_INPUT
        )
        self.length_menu.set("6 chiffres")
        self.length_menu.grid(row=1, column=0, sticky="ew")

        # Col 2: Plage de recherche (visible en mode numérique)
        self.range_col = ctk.CTkFrame(self.top_grid, fg_color="transparent")
        self.range_col.grid(row=0, column=2, sticky="ew")
        self.range_col.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.range_col,
            text="Plage de recherche",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        range_inputs = ctk.CTkFrame(self.range_col, fg_color="transparent")
        range_inputs.grid(row=1, column=0, sticky="ew")
        range_inputs.grid_columnconfigure(0, weight=1)
        range_inputs.grid_columnconfigure(1, weight=0)
        range_inputs.grid_columnconfigure(2, weight=1)

        self.start_entry = ctk.CTkEntry(
            range_inputs,
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_MONO, 13),
            height=40,
            corner_radius=RADIUS_INPUT,
            width=92
        )
        self.start_entry.insert(0, "000000")
        self.start_entry.grid(row=0, column=0, sticky="ew")
        self.start_entry.bind("<KeyRelease>", self._on_manual_edit)

        ctk.CTkLabel(
            range_inputs,
            text="  à  ",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=1)

        self.end_entry = ctk.CTkEntry(
            range_inputs,
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_MONO, 13),
            height=40,
            corner_radius=RADIUS_INPUT,
            width=92
        )
        self.end_entry.insert(0, "999999")
        self.end_entry.grid(row=0, column=2, sticky="ew")
        self.end_entry.bind("<KeyRelease>", self._on_manual_edit)

        # Contextual Panel for non-range methods (Section 9.2: only show applicable fields)
        self.context_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.context_frame.grid_columnconfigure(0, weight=1)

        self.context_lbl = ctk.CTkLabel(
            self.context_frame,
            text="",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.context_lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))

        ctx_row = ctk.CTkFrame(self.context_frame, fg_color="transparent")
        ctx_row.grid(row=1, column=0, sticky="ew")
        ctx_row.grid_columnconfigure(0, weight=1)

        self.context_entry = ctk.CTkEntry(
            ctx_row,
            placeholder_text="Ex: 000452 ou 123456, 4827??",
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_MONO, 13),
            height=40,
            corner_radius=RADIUS_INPUT
        )
        self.context_entry.grid(row=0, column=0, sticky="ew")
        self.context_entry.bind("<KeyRelease>", self._on_manual_edit)

        self.import_btn = ctk.CTkButton(
            ctx_row,
            text="Importer .txt",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_TEXT_WHITE,
            height=40,
            width=120,
            corner_radius=RADIUS_INPUT,
            command=self._import_txt_file
        )

        # 9.5 Checkboxes Row (Optimiser multithread / Arrêter à la première correspondance)
        chk_frame = ctk.CTkFrame(self, fg_color="transparent")
        chk_frame.grid(row=3, column=0, sticky="ew", padx=22, pady=(2, 8))

        self.opt_threads_chk = ctk.CTkCheckBox(
            chk_frame,
            text="Optimiser la recherche (multithread)",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            fg_color=COLOR_PRIMARY_BLUE,
            border_color=COLOR_CARD_BORDER,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5
        )
        self.opt_threads_chk.select()
        self.opt_threads_chk.grid(row=0, column=0, padx=(0, 20), pady=2, sticky="w")

        self.stop_first_chk = ctk.CTkCheckBox(
            chk_frame,
            text="Arrêter à la première correspondance",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            fg_color=COLOR_PRIMARY_BLUE,
            border_color=COLOR_CARD_BORDER,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5
        )
        self.stop_first_chk.select()
        self.stop_first_chk.grid(row=0, column=1, pady=2, sticky="w")

        # Helper info line
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=4, column=0, sticky="ew", padx=22, pady=(0, 16))
        self.info_frame.grid_columnconfigure(1, weight=1)

        self.info_icon = get_icon("info_circle", 15, COLOR_CYAN)
        info_ic_lbl = ctk.CTkLabel(self.info_frame, image=self.info_icon, text="")
        info_ic_lbl.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.info_text = ctk.CTkLabel(
            self.info_frame,
            text="Le programme testera toutes les combinaisons de 000000 à 999999.",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.info_text.grid(row=0, column=1, sticky="ew")

    def set_method(self, method_name: str, preset_value: str = ""):
        if method_name in self.METHODS:
            self.method_menu.set(method_name)
            self._on_method_selected(method_name)
            if preset_value:
                self.context_entry.delete(0, "end")
                self.context_entry.insert(0, preset_value)
                self._update_info_text()

    def _on_method_selected(self, choice: str):
        self.current_method = choice
        if choice in ("Codes numériques", "Codes numériques (0-9)"):
            self.context_frame.grid_remove()
            self.len_col.grid(row=0, column=1, sticky="ew", padx=(0, 12))
            self.range_col.grid(row=0, column=2, sticky="ew")
        else:
            self.len_col.grid_remove()
            self.range_col.grid_remove()
            self.context_frame.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 8))

            self.context_entry.delete(0, "end")
            if choice == "Mot de passe candidat":
                self.context_lbl.configure(text="Mot de passe candidat à vérifier :")
                self.context_entry.configure(placeholder_text="Saisissez le mot de passe candidat (ex: 000452)...")
                self.import_btn.grid_remove()
            elif choice == "Liste de mots de passe":
                self.context_lbl.configure(text="Liste de mots de passe candidats (séparés par virgule ou fichier .txt) :")
                self.context_entry.configure(placeholder_text="Ex: 123456, 000452, 202400...")
                self.context_entry.insert(0, "123456, 000452, 202400")
                self.import_btn.grid(row=0, column=1, padx=(10, 0))
            elif choice in ("Motif partiel (?)", "Mot de passe partiellement connu (?)"):
                self.context_lbl.configure(text="Motif avec caractères inconnus '?' (chaque '?' = 1 chiffre inconnu, max 5 '?') :")
                self.context_entry.configure(placeholder_text="Ex: 4827?? ou 2024??")
                self.context_entry.insert(0, "4827??")
                self.import_btn.grid_remove()

        self._update_info_text()

    def _import_txt_file(self):
        txt_path = filedialog.askopenfilename(
            title="Importer une liste de mots de passe (.txt)",
            filetypes=[("Fichiers texte (*.txt)", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if not txt_path:
            return
        try:
            raw = Path(txt_path).read_text(encoding="utf-8", errors="ignore").strip()
            items = [line.strip() for line in raw.replace("\r", "\n").split("\n") if line.strip()]
            joined = ", ".join(items)
            self.context_entry.delete(0, "end")
            self.context_entry.insert(0, joined)
            self._update_info_text()
        except Exception:
            pass

    def _on_length_selected(self, choice: str):
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
        self._update_info_text()

    def _on_manual_edit(self, event=None):
        self._update_info_text()

    def _update_info_text(self):
        if self.current_method in ("Codes numériques", "Codes numériques (0-9)"):
            s = self.start_entry.get().strip()
            e = self.end_entry.get().strip()
            if not s.isdigit() or not e.isdigit() or len(s) != len(e):
                self.info_text.configure(
                    text="Format attendu : deux nombres de même longueur (ex: 000000 à 999999).",
                    text_color=COLOR_ERROR_RED
                )
            else:
                self.info_text.configure(
                    text=f"Le programme testera toutes les combinaisons de {s} à {e}.",
                    text_color=COLOR_TEXT_MUTED
                )
        elif self.current_method == "Mot de passe candidat":
            val = self.context_entry.get().strip()
            if val:
                self.info_text.configure(
                    text="Vérification directe et instantanée du mot de passe candidat saisi.",
                    text_color=COLOR_TEXT_MUTED
                )
            else:
                self.info_text.configure(
                    text="Veuillez saisir un mot de passe candidat à vérifier.",
                    text_color=COLOR_TEXT_MUTED
                )
        else:
            raw = self.context_entry.get().strip()
            cands, err = CrackerEngine.build_targeted_candidates(raw)
            if err:
                self.info_text.configure(text=err, text_color=COLOR_ERROR_RED)
            else:
                cnt = f"{len(cands):,}".replace(",", " ")
                self.info_text.configure(
                    text=f"Prêt à tester {cnt} combinaison(s) ciblée(s) unique(s).",
                    text_color=COLOR_TEXT_MUTED
                )

        if self.on_params_changed:
            self.on_params_changed()

    def use_multithread(self) -> bool:
        return bool(self.opt_threads_chk.get())

    def get_search_bounds(self):
        s_str = self.start_entry.get().strip()
        e_str = self.end_entry.get().strip()
        try:
            if not s_str.isdigit() or not e_str.isdigit():
                raise ValueError("Non numérique")
            s_val = int(s_str)
            e_val = int(e_str)
            digits = max(len(s_str), len(e_str))
            return s_val, e_val, digits, s_str.zfill(digits), e_str.zfill(digits)
        except ValueError:
            return -1, -2, 6, s_str, e_str

    def get_context_value(self) -> str:
        return self.context_entry.get().strip()

    def set_compact_labels(self, compact: bool):
        self.len_title_lbl.configure(text="Longueur" if compact else "Longueur du mot de passe")

    def set_compact_vertical(self, compact: bool):
        self.header_frame.grid_configure(pady=(10, 6) if compact else (18, 12))
        self.top_grid.grid_configure(pady=(0, 6) if compact else (0, 10))
        self.info_frame.grid_configure(pady=(0, 10) if compact else (0, 16))
        h = 34 if compact else 40
        self.method_menu.configure(height=h)
        self.length_menu.configure(height=h)
        self.start_entry.configure(height=h)
        self.end_entry.configure(height=h)
