#!/usr/bin/env python3
"""
Générateur de clés de licence hors-ligne pour PDF Unlocker Desktop Windows.
Usage vendeur :
  python generate_license.py --tier PRO --email client@domaine.com
  python generate_license.py --tier BIZ --email entreprise@domaine.com
"""

import argparse
from core.license_manager import LicenseManager


def main():
    parser = argparse.ArgumentParser(description="Générateur de clés de licence PDF Unlocker Desktop")
    parser.add_argument("--tier", choices=["PRO", "BIZ"], default="PRO", help="Type de licence (PRO ou BIZ)")
    parser.add_argument("--email", default="demo@pdfunlocker.com", help="Email ou identifiant du client")
    args = parser.parse_args()

    key = LicenseManager.generate_key(tier=args.tier, seed=args.email)
    valid, tier_label, msg = LicenseManager.verify_key(key)
    print("====================================================")
    print(f"  PDF Unlocker Desktop — Générateur de Licence")
    print("====================================================")
    print(f"  Client / Seed : {args.email}")
    print(f"  Édition       : {tier_label}")
    print(f"  Clé générée   : {key}")
    print(f"  Vérification  : {msg} (Valide={valid})")
    print("====================================================")


if __name__ == "__main__":
    main()

