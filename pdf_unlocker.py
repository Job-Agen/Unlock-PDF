"""
PDF Unlocker MVP 1.0 — Application de vérification et récupération ciblée de mot de passe PDF.
Comporte quatre fonctions essentielles :
  1. Vérification du mot de passe candidat
  2. Récupération ciblée (liste de codes probables, souvenirs partiels avec '?', ou plage numérique)
  3. Enregistrement d'une copie déchiffrée du PDF
  4. Interface professionnelle sombre avec suivi de progression et gestion des erreurs.

Important : aucun logiciel ne peut garantir la récupération de tous les mots de passe.
Les performances dépendent notamment du type de chiffrement et de la complexité du mot de passe.
"""

import sys
import time
import argparse
from pathlib import Path

from ui.app import PDFUnlockerApp
from core.engine import CrackerEngine


def run_cli_mode(
    pdf_file: str = "document.pdf",
    verify_pwd: str = None,
    candidates_str: str = None,
    digits: int = 6,
    output_file: str = None
):
    """Mode console en ligne de commande pour PDF Unlocker MVP 1.0."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    engine = CrackerEngine()
    is_valid, is_encrypted, size_str, msg = engine.check_pdf_status(pdf_file)
    if not is_valid:
        print(f"✗ Erreur : {msg}")
        return
    if not is_encrypted:
        print(f"ℹ {msg}")
        return

    print(f"=== PDF Unlocker MVP 1.0 (CLI) ===")
    print(f"Document : {pdf_file} ({size_str})")
    print(f"Diagnostic : {engine.detect_encryption_details(pdf_file)}")

    # Fonctionnalité 1 : Vérification d'un mot de passe candidat unique
    if verify_pwd is not None:
        ok, v_msg = engine.verify_candidate_password(pdf_file, verify_pwd)
        if ok:
            print(f"✓ {v_msg}")
            out_path = engine.decrypt_and_save_pdf(pdf_file, verify_pwd, output_file)
            print(f"✓ Copie déverrouillée enregistrée : {out_path}")
        else:
            print(f"✗ {v_msg}")
        return

    # Fonctionnalité 2 : Récupération ciblée par liste / souvenirs partiels
    if candidates_str:
        p_cand = Path(candidates_str)
        raw_text = p_cand.read_text(encoding="utf-8") if p_cand.exists() else candidates_str
        candidates, err = engine.build_targeted_candidates(raw_text, expand_variants=True)
        if err:
            print(f"✗ Erreur : {err}")
            return

        print(f"--- Récupération ciblée sur {len(candidates)} candidats ---")
        debut = time.time()
        for idx, pwd in enumerate(candidates, 1):
            ok, _ = engine.verify_candidate_password(pdf_file, pwd)
            if ok:
                print(f"\n✓ Mot de passe trouvé : {pwd} (en {time.time() - debut:.2f}s, {idx} essais)")
                out_path = engine.decrypt_and_save_pdf(pdf_file, pwd, output_file)
                print(f"✓ Copie déverrouillée enregistrée : {out_path}")
                return
        print("✗ Aucun mot de passe trouvé parmi les candidats fournis.")
        return

    # Fonctionnalité 2 (Plage numérique par défaut)
    print(f"--- Recherche numérique sur {pdf_file} ({digits} chiffres) ---")
    debut = time.time()
    total = 10 ** digits
    fmt = f"{{:0{digits}d}}"

    for numero in range(total):
        mot_de_passe = fmt.format(numero)
        ok, _ = engine.verify_candidate_password(pdf_file, mot_de_passe)
        if ok:
            print(f"\n✓ Mot de passe trouvé : {mot_de_passe}")
            print(f"Temps écoulé : {time.time() - debut:.2f} secondes")
            out_path = engine.decrypt_and_save_pdf(pdf_file, mot_de_passe, output_file)
            print(f"✓ Copie déverrouillée enregistrée : {out_path}")
            return

        if numero % 5000 == 0 and numero > 0:
            pct = (numero / total) * 100
            print(f"Progression : {pct:.1f}% ({numero:,} essais)")

    print("✗ Aucun mot de passe trouvé.")


def main():
    parser = argparse.ArgumentParser(
        description="PDF Unlocker MVP 1.0 — Vérification, Récupération Ciblée & Déverrouillage PDF"
    )
    parser.add_argument("--cli", action="store_true", help="Exécuter en mode console sans interface graphique")
    parser.add_argument("--file", type=str, default="document.pdf", help="Chemin du fichier PDF")
    parser.add_argument("--verify", type=str, default=None, help="Fonction 1 : Vérifier un mot de passe candidat")
    parser.add_argument("--candidates", type=str, default=None, help="Fonction 2 : Liste de candidats (séparés par virgule ou chemin .txt)")
    parser.add_argument("--digits", type=int, default=6, help="Nombre de chiffres en mode plage (ex: 6)")
    parser.add_argument("--output", type=str, default=None, help="Fonction 3 : Chemin de sortie du PDF déverrouillé")

    args, _ = parser.parse_known_args()

    if args.cli:
        run_cli_mode(
            pdf_file=args.file,
            verify_pwd=args.verify,
            candidates_str=args.candidates,
            digits=args.digits,
            output_file=args.output
        )
    else:
        app = PDFUnlockerApp()
        app.mainloop()


if __name__ == "__main__":
    main()
