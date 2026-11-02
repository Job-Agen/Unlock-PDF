"""
Settings View (Page Paramètres — Section 17 of Master Prompt & Reference Image 1).
Sections: Général, Interface, Traitement, Confidentialité, Licence & Activation hors-ligne.
Saves changes explicitly when the user clicks 'Enregistrer' or activates a license key.
"""

import os
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from ui.theme import (
    COLOR_BG_ROOT, COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_PRIMARY_BLUE,
    COLOR_PRIMARY_HOVER, COLOR_SECONDARY_BTN, COLOR_SECONDARY_HOVER,
    COLOR_SUCCESS_TEXT, COLOR_SUCCESS_BTN, COLOR_SUCCESS_BTN_HOVER,
    COLOR_WARNING_AMBER, COLOR_ERROR_RED, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_INPUT_BG, FONT_FAMILY, FONT_MONO, MAIN_MARGIN_X, MAIN_MARGIN_Y
)
from core.settings_manager import SettingsManager
from core.license_manager import LicenseManager


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, settings: SettingsManager, on_license_changed=None, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_ROOT, corner_radius=0, **kwargs)
        self.settings = settings
        self.on_license_changed = on_license_changed
        self._build_ui()
        self.refresh_license_ui()

    def _build_ui(self):
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=MAIN_MARGIN_X, pady=MAIN_MARGIN_Y)

        # Header
        ctk.CTkLabel(
            container,
            text="Paramètres",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w")

        ctk.CTkLabel(
            container,
            text="Configurez les préférences générales, le traitement multithread, la confidentialité et votre licence.",
            font=(FONT_FAMILY, 13),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(3, 18))

        # 1. Section Général & Interface
        c_gen = self._make_section_card(container, "Général & Interface")

        row_theme = ctk.CTkFrame(c_gen, fg_color="transparent")
        row_theme.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(row_theme, text="Thème de l'application :", font=(FONT_FAMILY, 13), text_color=COLOR_TEXT_WHITE, width=220, anchor="w").pack(side="left")
        ctk.CTkLabel(row_theme, text="Sombre Professionnel (Référence Windows)", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_PRIMARY_BLUE).pack(side="left")

        row_lang = ctk.CTkFrame(c_gen, fg_color="transparent")
        row_lang.pack(fill="x", padx=20, pady=(0, 14))
        ctk.CTkLabel(row_lang, text="Langue de l'interface :", font=(FONT_FAMILY, 13), text_color=COLOR_TEXT_WHITE, width=220, anchor="w").pack(side="left")
        self.lang_menu = ctk.CTkOptionMenu(
            row_lang,
            values=["Français"],
            fg_color=COLOR_INPUT_BG,
            button_color="#162947",
            text_color=COLOR_TEXT_WHITE,
            width=200,
            height=36
        )
        self.lang_menu.set("Français")
        self.lang_menu.pack(side="left")

        # 2. Section Traitement
        c_proc = self._make_section_card(container, "Traitement & Performances")

        current_threads = self.settings.get("num_threads", 4)
        self.threads_lbl = ctk.CTkLabel(
            c_proc,
            text=f"Nombre de threads parallèles : {current_threads} (augmente la vitesse de vérification selon votre processeur)",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_TEXT_WHITE
        )
        self.threads_lbl.pack(anchor="w", padx=20, pady=(0, 6))

        cpu_max = max(8, os.cpu_count() or 8)
        self.threads_slider = ctk.CTkSlider(
            c_proc,
            from_=1,
            to=cpu_max,
            number_of_steps=cpu_max - 1,
            progress_color=COLOR_PRIMARY_BLUE,
            button_color=COLOR_PRIMARY_BLUE,
            command=self._on_slider_move
        )
        self.threads_slider.set(current_threads)
        self.threads_slider.pack(fill="x", padx=20, pady=(0, 14))

        out_row = ctk.CTkFrame(c_proc, fg_color="transparent")
        out_row.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(out_row, text="Dossier de sortie par défaut :", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 4))

        out_sub = ctk.CTkFrame(out_row, fg_color="transparent")
        out_sub.pack(fill="x")
        self.out_dir_entry = ctk.CTkEntry(
            out_sub,
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_FAMILY, 12),
            height=38
        )
        default_dir = self.settings.get("default_output_dir", str(Path.home() / "Documents"))
        self.out_dir_entry.insert(0, default_dir)
        self.out_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            out_sub,
            text="Parcourir",
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            height=38,
            width=110,
            command=self._browse_output_dir
        ).pack(side="right")

        self.sound_chk = ctk.CTkCheckBox(
            c_proc,
            text="Émettre un signal sonore discret lorsqu'un mot de passe est retrouvé",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_WHITE,
            fg_color=COLOR_PRIMARY_BLUE
        )
        if self.settings.get("play_sound", True):
            self.sound_chk.select()
        self.sound_chk.pack(anchor="w", padx=20, pady=(4, 6))

        self.decrypt_chk = ctk.CTkCheckBox(
            c_proc,
            text="Créer automatiquement une copie déchiffrée (_sans_mot_de_passe.pdf) lors d'une réussite",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_WHITE,
            fg_color=COLOR_PRIMARY_BLUE
        )
        if self.settings.get("auto_decrypt_copy", False):
            self.decrypt_chk.select()
        self.decrypt_chk.pack(anchor="w", padx=20, pady=(4, 16))

        # 3. Section Confidentialité
        c_priv = self._make_section_card(container, "Confidentialité & Données Locales")

        self.history_chk = ctk.CTkCheckBox(
            c_priv,
            text="Conserver l'historique local des opérations (les mots de passe ne sont jamais enregistrés en clair)",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_WHITE,
            fg_color=COLOR_PRIMARY_BLUE
        )
        if self.settings.get("enable_local_history", False):
            self.history_chk.select()
        self.history_chk.pack(anchor="w", padx=20, pady=(0, 16))

        # 4. Section Licence & Activation Hors-Ligne (Section 17 & PRD Section 13.2)
        c_lic = self._make_section_card(container, "Licence & Activation (Hors-Ligne)")

        self.lic_status_lbl = ctk.CTkLabel(
            c_lic,
            text="",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_WARNING_AMBER
        )
        self.lic_status_lbl.pack(anchor="w", padx=20, pady=(0, 8))

        lic_input_row = ctk.CTkFrame(c_lic, fg_color="transparent")
        lic_input_row.pack(fill="x", padx=20, pady=(0, 10))

        self.lic_entry = ctk.CTkEntry(
            lic_input_row,
            placeholder_text="Format : PDFU-PRO-XXXX-XXXX-XXXX",
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_MONO, 13),
            height=40,
            corner_radius=8
        )
        saved_key = self.settings.get("license_key", "")
        if saved_key:
            self.lic_entry.insert(0, saved_key)
        self.lic_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.activate_btn = ctk.CTkButton(
            lic_input_row,
            text="Activer la licence",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_SUCCESS_BTN,
            hover_color=COLOR_SUCCESS_BTN_HOVER,
            text_color="#FFFFFF",
            height=40,
            width=155,
            corner_radius=8,
            command=self._activate_license
        )
        self.activate_btn.pack(side="left", padx=(0, 8))

        self.demo_key_btn = ctk.CTkButton(
            lic_input_row,
            text="Insérer clé Pro de test",
            font=(FONT_FAMILY, 11),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_TEXT_MUTED,
            height=40,
            width=155,
            corner_radius=8,
            command=self._fill_demo_pro_key
        )
        self.demo_key_btn.pack(side="left", padx=(0, 8))

        self.deactivate_btn = ctk.CTkButton(
            lic_input_row,
            text="Désactiver",
            font=(FONT_FAMILY, 11),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color="#2A0E17",
            text_color=COLOR_ERROR_RED,
            height=40,
            width=95,
            corner_radius=8,
            command=self._deactivate_license
        )
        self.deactivate_btn.pack(side="left")

        ctk.CTkLabel(
            c_lic,
            text="• Édition Free (0 €) : Vérification manuelle illimitée + Essai jusqu'à 50 candidats ciblés.\n"
                 "• Édition Pro (19,90 €) / Business (49,90 €) : Plages numériques complètes, listes .txt illimitées et traitement par lots.",
            font=(FONT_FAMILY, 11),
            text_color=COLOR_TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 16))

        # Bottom Save Button
        save_row = ctk.CTkFrame(container, fg_color="transparent")
        save_row.pack(fill="x", pady=(6, 12))

        self.save_btn = ctk.CTkButton(
            save_row,
            text="Enregistrer les paramètres",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=44,
            width=220,
            corner_radius=10,
            command=self._save_all
        )
        self.save_btn.pack(side="right")

    def _make_section_card(self, parent, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        card.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(
            card,
            text=title,
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w", padx=20, pady=(16, 12))
        return card

    def refresh_license_ui(self):
        st = LicenseManager.get_license_status(self.settings)
        if st["is_pro"]:
            self.lic_status_lbl.configure(
                text=f"✓ Version : PDF Unlocker Desktop v1.0.0   •   Statut : Licence {st['tier']} Active ({st['license_key']})",
                text_color=COLOR_SUCCESS_TEXT
            )
        else:
            self.lic_status_lbl.configure(
                text="Version : PDF Unlocker Desktop v1.0.0   •   Statut : Édition Free (Essai 50 candidats)",
                text_color=COLOR_WARNING_AMBER
            )

    def _fill_demo_pro_key(self):
        demo_key = LicenseManager.generate_key(tier="PRO", seed="DEMO-CLIENT-2026")
        self.lic_entry.delete(0, "end")
        self.lic_entry.insert(0, demo_key)
        self._activate_license()

    def _activate_license(self):
        key_val = self.lic_entry.get().strip().upper()
        ok, tier, msg = LicenseManager.verify_key(key_val)
        if ok:
            self.settings.set("license_key", key_val)
            self.settings.set("license_tier", tier.lower())
            self.refresh_license_ui()
            if self.on_license_changed:
                self.on_license_changed()
            messagebox.showinfo("Licence activée", f"{msg}\nToutes les fonctionnalités Pro sont désormais débloquées.")
        else:
            messagebox.showerror("Clé invalide", msg)

    def _deactivate_license(self):
        self.settings.set("license_key", "")
        self.settings.set("license_tier", "free")
        self.lic_entry.delete(0, "end")
        self.refresh_license_ui()
        if self.on_license_changed:
            self.on_license_changed()

    def _on_slider_move(self, value):
        val = int(round(value))
        self.threads_lbl.configure(
            text=f"Nombre de threads parallèles : {val} (augmente la vitesse de vérification selon votre processeur)"
        )

    def _browse_output_dir(self):
        d = filedialog.askdirectory(title="Choisir le dossier de sortie par défaut")
        if d:
            self.out_dir_entry.delete(0, "end")
            self.out_dir_entry.insert(0, d)

    def _save_all(self):
        self.settings.set("num_threads", int(round(self.threads_slider.get())))
        self.settings.set("default_output_dir", self.out_dir_entry.get().strip())
        self.settings.set("play_sound", bool(self.sound_chk.get()))
        self.settings.set("auto_decrypt_copy", bool(self.decrypt_chk.get()))
        self.settings.set("enable_local_history", bool(self.history_chk.get()))
        messagebox.showinfo("Paramètres enregistrés", "Vos préférences ont été enregistrées avec succès.")
