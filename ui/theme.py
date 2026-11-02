"""
Centralized UI Theme & Design System for PDF Unlocker Desktop Windows.
Strictly implements Section 2 (Palette, Typography, Radii) and Section 3 (Dimensions)
of the Master Specification and Reference Mockups.
"""

import sys
from pathlib import Path

# ==========================================
# 2.2. PALETTE DE COULEURS OFFICIELLE
# ==========================================
COLOR_BG_ROOT = "#061225"          # Fond principal : Bleu nuit profond
COLOR_TOPBAR_BG = "#0B1930"        # Barre supérieure : Bleu nuit
COLOR_SIDEBAR_BG = "#08162C"       # Barre latérale : Bleu sombre
COLOR_FOOTER_BG = "#08152A"        # Barre inférieure : Bleu nuit sombre

COLOR_CARD_BG = "#0B1A31"          # Fond des cartes : Bleu sombre
COLOR_CARD_SECONDARY = "#0D2040"   # Fond secondaire des cartes : Bleu profond
COLOR_CARD_BORDER = "#1B3559"      # Bordures : Bleu gris sombre (1 px)

COLOR_TEXT_WHITE = "#F3F7FF"       # Texte principal : Blanc légèrement bleuté
COLOR_TEXT_MUTED = "#9BB9E3"       # Texte secondaire : Bleu gris clair
COLOR_TEXT_DIM = "#6F91BD"         # Texte discret : Bleu gris

COLOR_PRIMARY_BLUE = "#1687F8"     # Bleu principal : Bleu électrique
COLOR_PRIMARY_HOVER = "#0872D9"    # Bleu de survol : Bleu plus foncé
COLOR_LOGO_BG = "#0876E8"          # Fond du carré logo barre supérieure
COLOR_CYAN = "#23B5FF"             # Cyan : Bleu lumineux

COLOR_SUCCESS_TEXT = "#16D18C"     # Vert de succès : Vert émeraude
COLOR_SUCCESS_BG = "#062A28"       # Fond du bloc de résultat positif
COLOR_SUCCESS_BORDER = "#087C5A"   # Bordure du bloc de résultat positif
COLOR_SUCCESS_BTN = "#10B981"      # Bouton d'action succès
COLOR_SUCCESS_BTN_HOVER = "#059669"

COLOR_ERROR_RED = "#FF5368"        # Rouge d'erreur : Rouge corail
COLOR_ERROR_BG = "#2A0E17"         # Fond du bloc d'erreur
COLOR_ERROR_BORDER = "#881D32"     # Bordure du bloc d'erreur

COLOR_WARNING_AMBER = "#F6B94A"    # Orange d'avertissement : Ambre

COLOR_INPUT_BG = "#081427"         # Fond des champs : Bleu presque noir
COLOR_SECONDARY_BTN = "#1B2D4E"    # Fond des boutons secondaires : Bleu ardoise
COLOR_SECONDARY_HOVER = "#253D65"  # Survol des boutons secondaires

# Navigation latérale
COLOR_NAV_ACTIVE_BG = "#103A82"    # Élément actif du menu
COLOR_NAV_HOVER_BG = "#122C4D"     # Survol élément inactif
COLOR_NAV_INACTIVE_TEXT = "#D8E6FC"

# Encadré Premium
COLOR_PROMO_BG = "#081F45"
COLOR_PROMO_BORDER = "#15468A"

# Carte de présentation (Hero Banner)
COLOR_HERO_BG = "#102B61"
COLOR_HERO_BG_ALT = "#10205A"
COLOR_HERO_BORDER = "#234C9A"
COLOR_HERO_TEXT = "#C5DAFB"

# Indicateurs de progression
COLOR_PROGRESS_CIRCLE_BG = "#142A4A"
COLOR_PROGRESS_TRACK = "#1A3155"

# ==========================================
# 2.3. TYPOGRAPHIE (Windows Native)
# ==========================================
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

FONT_SIZE_APP_TITLE = 22           # Titre de l'application (Semi-gras)
FONT_SIZE_HERO_TITLE = 27          # Titre de la page principale (Gras)
FONT_SIZE_CARD_TITLE = 15          # Titres des cartes (Semi-gras)
FONT_SIZE_SUBTITLE = 14            # Sous-titres
FONT_SIZE_BODY = 13                # Texte principal
FONT_SIZE_SECONDARY = 12           # Texte secondaire
FONT_SIZE_META = 11                # Métadonnées et horodatages
FONT_SIZE_RESULT_VALUE = 32        # Valeur importante du résultat (Gras)

# ==========================================
# 2.4. FORMES ET RAYONS (px)
# ==========================================
RADIUS_CARD_PRIMARY = 14           # Cartes principales : 13-15 px
RADIUS_CARD_SECONDARY = 11         # Cartes secondaires : 10-12 px
RADIUS_BTN_PRIMARY = 10            # Boutons principaux : 9-10 px
RADIUS_INPUT = 8                   # Champs de saisie : 8-9 px
RADIUS_BADGE = 7                   # Badge de statut : 6-8 px
RADIUS_ICON_BOX = 12               # Icônes dans des conteneurs : 10-14 px
RADIUS_LOGO_BOX = 14               # Carré logo barre supérieure : 14 px
RADIUS_NAV_ITEM = 10               # Élément de navigation : 10 px

# ==========================================
# 3.1. DIMENSIONS DE LA FENÊTRE WINDOWS
# ==========================================
WINDOW_INITIAL_WIDTH = 1536
WINDOW_INITIAL_HEIGHT = 1024
WINDOW_MIN_WIDTH = 1120
WINDOW_MIN_HEIGHT = 760

TOPBAR_HEIGHT = 84
SIDEBAR_WIDTH = 268
SIDEBAR_COMPACT_WIDTH = 238
FOOTER_HEIGHT = 40

MAIN_MARGIN_X = 24
MAIN_MARGIN_Y = 24
COLUMN_GAP = 22


def get_resource_path(relative_path: str) -> Path:
    """Resolves bundled asset paths both in dev mode and inside a PyInstaller .exe."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base_path / relative_path
