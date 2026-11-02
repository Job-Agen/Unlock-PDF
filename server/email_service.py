"""
Service d'envoi et de rendu des e-mails transactionnels pour les licences PDF Unlocker.
Génère des e-mails soignés (HTML responsive et version texte brut) comprenant la clé de licence,
les instructions d'activation étape par étape et le rappel de la garantie 14 jours.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict


def build_license_email_html(customer_name: str, license_key: str, tier: str, download_url: str) -> str:
    tier_label = "Pro" if "PRO" in tier.upper() else "Business"
    clean_name = customer_name.strip() if customer_name else "Cher client"

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Votre licence {tier_label} — PDF Unlocker Desktop</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #030e23; color: #ffffff; margin: 0; padding: 24px; line-height: 1.6;">
  <div style="max-width: 600px; margin: 0 auto; background-color: #081a38; border: 1px solid #1f4273; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    
    <!-- En-tête -->
    <div style="background: linear-gradient(135deg, #0078f2, #004bb5); padding: 28px 24px; text-align: center;">
      <h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">PDF Unlocker Desktop</h1>
      <p style="margin: 6px 0 0; font-size: 14px; color: #cbe0ff;">Confirmation d'achat & Clé d'activation officielle</p>
    </div>

    <!-- Corps du message -->
    <div style="padding: 28px 24px;">
      <p style="font-size: 15px; color: #d0e2fc; margin-top: 0;">Bonjour <strong>{clean_name}</strong>,</p>
      <p style="font-size: 14.5px; color: #a9c6ee;">
        Merci pour votre commande ! Votre licence perpétuelle <strong>PDF Unlocker {tier_label}</strong> est désormais active et prête à être utilisée sur votre machine Windows.
      </p>

      <!-- Encadré Clé de Licence -->
      <div style="background-color: #041026; border: 2px dashed #0099ff; border-radius: 10px; padding: 20px; text-align: center; margin: 24px 0;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 700; color: #729bcf; letter-spacing: 1px; display: block; margin-bottom: 8px;">Votre Clé de Licence Hors-Ligne :</span>
        <code style="font-family: 'Consolas', 'Courier New', monospace; font-size: 20px; font-weight: 800; color: #10d68a; letter-spacing: 1px; word-break: break-all;">{license_key}</code>
      </div>

      <!-- Bouton Téléchargement -->
      <div style="text-align: center; margin: 28px 0;">
        <a href="{download_url}" style="display: inline-block; background: linear-gradient(135deg, #0582f6, #0066d6); color: #ffffff; font-size: 14px; font-weight: 700; text-decoration: none; padding: 12px 28px; border-radius: 8px; box-shadow: 0 4px 14px rgba(0,120,242,0.4);">
          ⬇ Télécharger PDF Unlocker pour Windows (.exe)
        </a>
      </div>

      <!-- Instructions d'activation -->
      <div style="background-color: #0b2246; border: 1px solid #1e3f6d; border-radius: 10px; padding: 18px 20px; margin: 24px 0;">
        <h3 style="margin: 0 0 10px; font-size: 14px; font-weight: 700; color: #ffffff;">Comment activer votre licence en 3 étapes :</h3>
        <ol style="margin: 0; padding-left: 20px; font-size: 13px; color: #c4dbf9; line-height: 1.7;">
          <li>Téléchargez et lancez <strong>PDF_Unlocker_MVP_1.0.exe</strong> (aucune installation nécessaire).</li>
          <li>Dans le menu latéral de gauche, cliquez sur <strong>⚙ Paramètres</strong>.</li>
          <li>Collez votre clé de licence dans le champ prévu et cliquez sur <strong>Activer ma licence</strong>.</li>
        </ol>
      </div>

      <!-- Note de confidentialité & Garantie -->
      <p style="font-size: 12px; color: #789bc4; line-height: 1.6; border-top: 1px solid #142f56; padding-top: 18px; margin-bottom: 0;">
        💡 <strong>100 % Hors-ligne :</strong> L'activation ne nécessite aucun accès à Internet grâce à notre moteur de signature cryptographique locale.<br>
        🛡️ <strong>Garantie de 14 jours :</strong> Vous disposez de notre garantie satisfait ou remboursé sous 14 jours en cas de difficulté technique sur votre système Windows.
      </p>
    </div>

    <!-- Pied de page -->
    <div style="background-color: #040e20; border-top: 1px solid #122849; padding: 18px 24px; text-align: center; font-size: 11.5px; color: #5879a3;">
      PDF Unlocker Desktop • Support technique : <a href="mailto:contact@pdfunlocker.com" style="color: #0084ff; text-decoration: none;">contact@pdfunlocker.com</a>
    </div>

  </div>
</body>
</html>"""


def build_license_email_text(customer_name: str, license_key: str, tier: str, download_url: str) -> str:
    tier_label = "Pro" if "PRO" in tier.upper() else "Business"
    clean_name = customer_name.strip() if customer_name else "Cher client"

    return f"""================================================================================
  PDF UNLOCKER DESKTOP — ACTIVATION OFFICIELLE {tier_label.upper()}
================================================================================

Bonjour {clean_name},

Merci pour votre achat ! Votre licence perpétuelle PDF Unlocker {tier_label} est active.

VOTRE CLÉ DE LICENCE HORS-LIGNE :
--------------------------------------------------------------------------------
{license_key}
--------------------------------------------------------------------------------

TÉLÉCHARGEMENT DU LOGICIEL :
Lien officiel : {download_url}

INSTRUCTIONS D'ACTIVATION EN 3 ÉTAPES :
1. Lancez PDF_Unlocker_MVP_1.0.exe sur votre PC Windows 10/11.
2. Cliquez sur "Paramètres" dans le menu de gauche.
3. Collez votre clé ci-dessus et cliquez sur "Activer ma licence".

Le traitement est 100 % local sur votre machine, sans connexion Internet requise.
Garantie de remboursement de 14 jours en cas d'incompatibilité technique.

Assistance technique : contact@pdfunlocker.com
================================================================================
"""


def send_license_email(
    to_email: str,
    customer_name: str,
    license_key: str,
    tier: str = "PRO",
    smtp_config: Optional[Dict[str, str]] = None,
    download_url: str = "https://pdfunlocker.com/dist/PDF_Unlocker_MVP_1.0.exe"
) -> bool:
    """
    Envoie l'e-mail contenant la clé de licence.
    Si la configuration SMTP n'est pas renseignée (mode TEST / LOCAL), affiche l'e-mail dans la console.
    """
    tier_label = "Pro" if "PRO" in tier.upper() else "Business"
    subject = f"Votre clé de licence PDF Unlocker {tier_label} [{license_key}]"

    html_content = build_license_email_html(customer_name, license_key, tier, download_url)
    text_content = build_license_email_text(customer_name, license_key, tier, download_url)

    if not smtp_config or not smtp_config.get("host"):
        print(f"\n[MODE SIMULATION] E-mail préparé pour {to_email} (aucun serveur SMTP configuré) :")
        print(f"Sujet : {subject}")
        print(f"Clé transmise : {license_key}")
        print("-" * 60)
        print(text_content)
        print("-" * 60 + "\n")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_config.get("from_email", "support@pdfunlocker.com")
        msg["To"] = to_email

        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        host = smtp_config["host"]
        port = int(smtp_config.get("port", 587))
        user = smtp_config.get("user")
        password = smtp_config.get("password")

        server = smtplib.SMTP(host, port, timeout=15)
        server.ehlo()
        if port == 587:
            server.starttls()
            server.ehlo()
        if user and password:
            server.login(user, password)
        server.sendmail(msg["From"], [to_email], msg.as_string())
        server.quit()
        print(f"[OK] E-mail de licence envoyé avec succès à {to_email}")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec de l'envoi SMTP à {to_email} : {e}")
        return False

