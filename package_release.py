#!/usr/bin/env python3
"""
Générateur de package de distribution zip pour PDF Unlocker Desktop Windows.
Crée une archive complète prête à distribuer avec :
 - L'exécutable autonome (.exe)
 - Le fichier de hachage SHA-256
 - Une notice d'utilisation et d'intégrité (README_DISTRIBUTION.txt)
"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
EXE_NAME = "PDF_Unlocker_MVP_1.0.exe"
SHA_NAME = "PDF_Unlocker_MVP_1.0.exe.sha256"
ZIP_NAME = "PDF_Unlocker_v1.0.0_Windows_x64.zip"


def create_distribution_package():
    exe_path = DIST / EXE_NAME
    sha_path = DIST / SHA_NAME

    if not exe_path.exists():
        raise FileNotFoundError(f"L'exécutable {exe_path} est introuvable. Exécutez d'abord build_windows.py.")

    sha256_content = sha_path.read_text(encoding="utf-8").strip() if sha_path.exists() else "N/A"

    readme_content = f"""================================================================================
  PDF UNLOCKER DESKTOP MVP 1.0 (Édition Windows 10/11 - 64 bits)
================================================================================

1. PRÉSENTATION
---------------
PDF Unlocker Desktop est une application 100 % locale et sécurisée permettant :
- De vérifier un mot de passe candidat sur un document PDF chiffré.
- D'exporter une copie déchiffrée sans mot de passe (_sans_mot_de_passe.pdf) sans
  jamais modifier le fichier original.
- De retrouver un mot de passe à partir d'indices partiels (motifs avec '?' et listes).
- De traiter plusieurs documents simultanément en mode batch.

Aucune donnée, aucun document et aucun mot de passe n'est envoyé sur Internet.

2. VÉRIFICATION D'INTÉGRITÉ SHA-256
-----------------------------------
Pour vérifier que l'exécutable n'a pas été altéré, ouvrez un terminal PowerShell
dans ce dossier et exécutez :

  Get-FileHash -Algorithm SHA256 .\\{EXE_NAME}

Empreinte officielle attendue :
  {sha256_content}

3. DÉMARRAGE RAPIDE
-------------------
Double-cliquez simplement sur '{EXE_NAME}' pour démarrer l'interface graphique.
Aucune installation de dépendance ni droits administrateur ne sont requis.

Mode ligne de commande (CLI) également supporté :
  .\\{EXE_NAME} --cli --file document.pdf --verify 000452 --output document_ouvert.pdf

4. ACTIVATION DE LICENCE (OPTIONNEL)
------------------------------------
Pour activer une édition Pro ou Business et lever le plafond des listes de candidats,
rendez-vous dans le menu "Paramètres" et saisissez votre clé de licence au format :
  PDFU-PRO-XXXX-XXXX-XXXX ou PDFU-BIZ-XXXX-XXXX-XXXX

5. CADRE LÉGAL, POLITIQUE DE REMBOURSEMENT & SUPPORT
---------------------------------------------------
- Utilisation légale : Le logiciel doit être utilisé exclusivement sur des documents dont
  vous êtes le propriétaire légitime ou pour lesquels vous avez une autorisation écrite.
- Confidentialité : Traitement 100 % hors-ligne, zéro transfert cloud, zéro secret consigné.
- Garantie de remboursement : Remboursement intégral possible sous 14 jours en cas
  d'incompatibilité technique avérée avec Windows 10/11 (sur envoi du diagnostic expurgé).
- Support technique : contact@pdfunlocker.com

================================================================================
"""

    readme_path = DIST / "README_DISTRIBUTION.txt"
    readme_path.write_text(readme_content, encoding="utf-8")

    zip_path = DIST / ZIP_NAME
    print(f"[*] Création du package de distribution {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe_path, arcname=EXE_NAME)
        if sha_path.exists():
            zf.write(sha_path, arcname=SHA_NAME)
        zf.write(readme_path, arcname="README_DISTRIBUTION.txt")

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Package prêt : {zip_path} ({size_mb:.2f} Mo)")


if __name__ == "__main__":
    create_distribution_package()

