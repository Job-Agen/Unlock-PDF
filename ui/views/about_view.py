"""
Help & About View (Page Aide — Section 6.2 & Section 25 of Master Prompt).
Displays usage instructions, encryption limitations, privacy guarantees, and legal terms.
"""

import customtkinter as ctk
from ui.theme import (
    COLOR_BG_ROOT, COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_CYAN,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, FONT_FAMILY, MAIN_MARGIN_X, MAIN_MARGIN_Y
)
from ui.icons import create_app_logo_image


class AboutView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_ROOT, corner_radius=0, **kwargs)
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=MAIN_MARGIN_X, pady=MAIN_MARGIN_Y)

        # Header Card
        header_card = ctk.CTkFrame(
            container,
            fg_color=COLOR_CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        header_card.pack(fill="x", pady=(0, 16))

        h_inner = ctk.CTkFrame(header_card, fg_color="transparent")
        h_inner.pack(fill="both", expand=True, padx=22, pady=20)

        self.logo_img = create_app_logo_image(56)
        ctk.CTkLabel(h_inner, image=self.logo_img, text="").pack(side="left", padx=(0, 18))

        h_text = ctk.CTkFrame(h_inner, fg_color="transparent")
        h_text.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(h_text, text="PDF Unlocker Desktop — Aide & Documentation", font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(h_text, text="Version 1.0.0 (Windows 10/11 — 64 bits) • Moteur local pikepdf / qpdf", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_CYAN).pack(anchor="w", pady=(2, 4))
        ctk.CTkLabel(h_text, text="Logiciel de vérification et de récupération ciblée de mots de passe pour vos documents PDF personnels.", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED).pack(anchor="w")

        # Guide Card
        f_card = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG, corner_radius=13, border_width=1, border_color=COLOR_CARD_BORDER)
        f_card.pack(fill="x", pady=(0, 16))

        f_inner = ctk.CTkFrame(f_card, fg_color="transparent")
        f_inner.pack(fill="both", expand=True, padx=22, pady=18)

        ctk.CTkLabel(f_inner, text="Comment utiliser PDF Unlocker Desktop", font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 10))

        steps = [
            "1. Sélectionnez votre document PDF protégé depuis la page « Accueil » ou « Déverrouiller ».",
            "2. Choisissez la méthode adaptée : Codes numériques (avec conservation des zéros initiaux ex: 000452), Mot de passe candidat, Liste de mots de passe (.txt) ou Motif partiellement connu ('?').",
            "3. Lancez l'opération : la progression circulaire, la vitesse et le journal s'actualisent en temps réel sans bloquer l'interface.",
            "4. Une fois le mot de passe validé, cliquez sur « Enregistrer une copie déchiffrée » pour obtenir un PDF standard sans mot de passe."
        ]
        for s in steps:
            ctk.CTkLabel(f_inner, text=s, font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED, justify="left", wraplength=780).pack(anchor="w", pady=3)

        # Limits & Privacy Card
        lim_card = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG, corner_radius=13, border_width=1, border_color=COLOR_CARD_BORDER)
        lim_card.pack(fill="x")

        lim_inner = ctk.CTkFrame(lim_card, fg_color="transparent")
        lim_inner.pack(fill="both", expand=True, padx=22, pady=18)

        ctk.CTkLabel(lim_inner, text="Confidentialité, Sécurité & Limites Techniques", font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(
            lim_inner,
            text="• Traitement 100 % local : vos documents PDF ne quittent jamais votre ordinateur.\n"
                 "• Protection des secrets : aucun mot de passe en clair n'est inscrit dans les journaux ni stocké dans l'historique permanent.\n"
                 "• Préservation des originaux : l'enregistrement d'une copie déchiffrée crée toujours un nouveau fichier vérifié sans modifier le PDF source.\n"
                 "• Transparence : aucun logiciel ne peut garantir la récupération de tous les mots de passe. Les performances dépendent du chiffrement du document (RC4, AES-128, AES-256) et de la précision des paramètres fournis.\n"
                 "• Usage autorisé uniquement : réservé aux documents dont vous êtes le propriétaire ou pour lesquels vous disposez d'une autorisation explicite.",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=780
        ).pack(anchor="w")
