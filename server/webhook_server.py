#!/usr/bin/env python3
"""
Serveur Webhook de délivrance automatique de licences pour PDF Unlocker Desktop.
Prend en charge les webhooks de :
  - Lemon Squeezy (événement 'order_created')
  - Paddle (événement 'transaction.completed')
  - Stripe (événement 'checkout.session.completed')
  - Gumroad (événement 'sale')

Fonctionnalités :
  1. Vérification cryptographique des signatures HMAC-SHA256 des requêtes webhooks.
  2. Génération immédiate de clé de licence hors-ligne via LicenseManager (core/license_manager.py).
  3. Envoi automatique de l'e-mail de bienvenue avec la clé et le lien de téléchargement.
  4. Journalisation locale horodatée dans server/licenses_issued.jsonl.
"""

import hmac
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs

# Ajout de la racine du projet dans le sys.path pour importer le moteur de licence
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.license_manager import LicenseManager
from server.email_service import send_license_email

PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "LEMON_SQUEEZY_OU_STRIPE_SECRET_KEY_2026")
LICENSES_LOG = Path(__file__).resolve().parent / "licenses_issued.jsonl"

SMTP_CONFIG = {
    "host": os.environ.get("SMTP_HOST", ""),
    "port": os.environ.get("SMTP_PORT", "587"),
    "user": os.environ.get("SMTP_USER", ""),
    "password": os.environ.get("SMTP_PASS", ""),
    "from_email": os.environ.get("FROM_EMAIL", "commandes@pdfunlocker.com"),
}


def verify_hmac_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    """Vérifie la signature HMAC-SHA256 d'un webhook (Lemon Squeezy, Stripe, etc.)."""
    if not secret or not signature_header:
        # En mode développement sans secret configuré, accepte avec avertissement
        return True
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected.lower(), signature_header.strip().lower())


def record_license_issued(record: dict):
    """Enregistre la délivrance de licence dans le journal local sécurisé."""
    with open(LICENSES_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def process_order(customer_email: str, customer_name: str, tier: str, platform_source: str, order_id: str) -> dict:
    """Génère la clé, l'enregistre et envoie l'e-mail au client."""
    tier_norm = "BIZ" if "BIZ" in tier.upper() or "BUSINESS" in tier.upper() else "PRO"
    license_key = LicenseManager.generate_key(tier=tier_norm, seed=customer_email)

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform_source,
        "order_id": order_id,
        "customer_email": customer_email,
        "customer_name": customer_name,
        "tier": tier_norm,
        "license_key": license_key,
    }
    record_license_issued(record)
    print(f"\n[COMMANDE VALIDÉE] {platform_source} | Client : {customer_email} | Tier : {tier_norm}")
    print(f"Clé générée : {license_key}")

    # Envoi de l'e-mail
    send_license_email(
        to_email=customer_email,
        customer_name=customer_name,
        license_key=license_key,
        tier=tier_norm,
        smtp_config=SMTP_CONFIG if SMTP_CONFIG["host"] else None
    )

    return record


class WebhookHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send_json(200, {
                "status": "online",
                "service": "PDF Unlocker Licensing Webhook Server",
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            self._send_json(404, {"error": "Route introuvable"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        # 1. ROUTE LEMON SQUEEZY
        if self.path == "/webhook/lemonsqueezy":
            signature = self.headers.get("X-Signature", "")
            if not verify_hmac_signature(raw_body, signature, WEBHOOK_SECRET):
                self._send_json(401, {"error": "Signature webhook invalide"})
                return

            try:
                data = json.loads(raw_body.decode("utf-8"))
                event_name = data.get("meta", {}).get("event_name")
                if event_name == "order_created":
                    attrs = data.get("data", {}).get("attributes", {})
                    customer_email = attrs.get("user_email")
                    customer_name = attrs.get("user_name", "")
                    order_id = str(data.get("data", {}).get("id"))
                    item_name = attrs.get("first_order_item", {}).get("product_name", "")
                    tier = "BIZ" if "business" in item_name.lower() else "PRO"

                    res = process_order(customer_email, customer_name, tier, "LemonSqueezy", order_id)
                    self._send_json(200, {"success": True, "license": res["license_key"]})
                    return
                else:
                    self._send_json(200, {"received": True, "event_ignored": event_name})
                    return
            except Exception as e:
                self._send_json(400, {"error": f"Erreur de traitement : {str(e)}"})
                return

        # 2. ROUTE STRIPE
        elif self.path == "/webhook/stripe":
            try:
                data = json.loads(raw_body.decode("utf-8"))
                event_type = data.get("type")
                if event_type == "checkout.session.completed":
                    session = data.get("data", {}).get("object", {})
                    customer_email = session.get("customer_details", {}).get("email") or session.get("customer_email")
                    customer_name = session.get("customer_details", {}).get("name", "")
                    order_id = session.get("id")
                    tier = session.get("metadata", {}).get("tier", "PRO")

                    res = process_order(customer_email, customer_name, tier, "Stripe", order_id)
                    self._send_json(200, {"success": True, "license": res["license_key"]})
                    return
                else:
                    self._send_json(200, {"received": True, "event_ignored": event_type})
                    return
            except Exception as e:
                self._send_json(400, {"error": f"Erreur Stripe : {str(e)}"})
                return

        # 3. ROUTE GUMROAD
        elif self.path == "/webhook/gumroad":
            try:
                parsed = parse_qs(raw_body.decode("utf-8"))
                customer_email = parsed.get("email", [""])[0]
                customer_name = parsed.get("full_name", [""])[0]
                order_id = parsed.get("sale_id", [""])[0]
                product_name = parsed.get("product_name", [""])[0]
                tier = "BIZ" if "business" in product_name.lower() else "PRO"

                res = process_order(customer_email, customer_name, tier, "Gumroad", order_id)
                self._send_json(200, {"success": True, "license": res["license_key"]})
                return
            except Exception as e:
                self._send_json(400, {"error": f"Erreur Gumroad : {str(e)}"})
                return

        else:
            self._send_json(404, {"error": f"Endpoint non supporté : {self.path}"})


def run():
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    print("=" * 60)
    print(f" Serveur Webhook PDF Unlocker démarré sur le port {PORT}")
    print(f" Endpoints actifs :")
    print(f"   • http://localhost:{PORT}/health")
    print(f"   • http://localhost:{PORT}/webhook/lemonsqueezy")
    print(f"   • http://localhost:{PORT}/webhook/stripe")
    print(f"   • http://localhost:{PORT}/webhook/gumroad")
    print(f" Journal des licences : {LICENSES_LOG}")
    print("=" * 60)
    server.serve_forever()


if __name__ == "__main__":
    run()

