#!/usr/bin/env python3
"""
Simulateur de test local pour le système de webhooks et délivrance de licence.
Permet de tester l'ensemble du flux sans dépendre d'une commande réelle.

Usage :
  python server/test_webhook.py --tier PRO --email client@domaine.com --name "Jean Dupont"
  python server/test_webhook.py --tier BIZ --email entreprise@cabinet.fr --name "Cabinet Legal"
"""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from server.webhook_server import process_order


def main():
    parser = argparse.ArgumentParser(description="Test du flux de délivrance automatique de licence")
    parser.add_argument("--tier", choices=["PRO", "BIZ"], default="PRO", help="Niveau de licence (PRO ou BIZ)")
    parser.add_argument("--email", default="client.test@exemple.com", help="Email du client")
    parser.add_argument("--name", default="Alice Martin", help="Nom du client")
    parser.add_argument("--platform", default="SimulationTest", help="Source d'achat (ex. LemonSqueezy, Stripe)")
    parser.add_argument("--order-id", default="ORDER-SIM-2026-999", help="Numéro de commande simulé")
    args = parser.parse_args()

    print("================================================================")
    print("  SIMULATION D'ACHAT ET DÉLIVRANCE AUTOMATIQUE DE LICENCE")
    print("================================================================")
    print(f"  Client    : {args.name} <{args.email}>")
    print(f"  Formule   : {args.tier}")
    print(f"  Plateforme: {args.platform}")
    print(f"  Commande  : {args.order_id}")
    print("================================================================")

    record = process_order(
        customer_email=args.email,
        customer_name=args.name,
        tier=args.tier,
        platform_source=args.platform,
        order_id=args.order_id
    )

    print("\n[RÉSULTAT DE L'OPÉRATION]")
    print(f"  Clé de licence générée : {record['license_key']}")
    print(f"  Horodatage UTC          : {record['timestamp_utc']}")
    print(f"  Enregistrement journal  : server/licenses_issued.jsonl")
    print("  Vérification de la clé :")
    from core.license_manager import LicenseManager
    valid, tier_label, msg = LicenseManager.verify_key(record['license_key'])
    print(f"    - Valide : {valid}")
    print(f"    - Édition: {tier_label}")
    print(f"    - Statut : {msg}")
    print("================================================================\n")


if __name__ == "__main__":
    main()

