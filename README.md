# PDF Unlocker MVP 1.0 (Édition Windows 10/11 — 64 bits)

Application de bureau locale pour **vérifier un mot de passe candidat**, **récupérer un accès à partir d'indices ciblés bornés** et **enregistrer une copie déchiffrée** de vos documents PDF sans jamais téléverser vos fichiers sur Internet.

---

## Pile Technologique (Conforme au PRD v1.0)

* **Plateforme cible** : Windows 10 / 11 (64 bits) — Traitement 100 % hors-ligne.
* **Langage & UI Desktop** : **Python** + **CustomTkinter** ([`pdf_unlocker.py`](pdf_unlocker.py), [`ui/app.py`](ui/app.py)).
* **Moteur PDF** : **`pikepdf` / `qpdf`** ([`core/engine.py`](core/engine.py)).
* **Stockage local** : **JSON** local sans données sensibles ([`core/settings_manager.py`](core/settings_manager.py), [`core/history_manager.py`](core/history_manager.py), historique désactivé par défaut).
* **Packaging Windows** : **PyInstaller** + empreinte **SHA-256** ([`build_windows.py`](build_windows.py)).

---

## Les 4 Fonctionnalités Essentielles du MVP 1.0

1. **Fonctionnalité 1 — Vérification du mot de passe (`FR-01` à `FR-04`)**
   * Diagnostic précis de l'état du PDF (`user_password_required`, `permissions_only`, `unencrypted`, `corrupted_or_invalid`, `unsupported_encryption`).
   * Validation stricte des codes à 6 chiffres (préservation des zéros initiaux ex. `000452`) ou test immédiat d'un mot de passe candidat.
2. **Fonctionnalité 2 — Récupération ciblée bornée (`FR-06` à `FR-09`)**
   * Import de listes `.txt` ou saisie de candidats probables avec déduplication automatique.
   * Motifs bornés avec joker `?` (plafond de sécurité : max 5 `?` et 100 000 combinaisons).
   * Progression en temps réel et bouton d'arrêt immédiat.
3. **Fonctionnalité 3 — Enregistrement du PDF déverrouillé (`FR-05`)**
   * Création d'une copie déchiffrée distincte (`_sans_mot_de_passe.pdf`), interdiction d'écraser le fichier original et vérification automatique par réouverture sans mot de passe.
4. **Fonctionnalité 4 — Interface sombre professionnelle & Confidentialité (`FR-10` à `FR-15`)**
   * Zéro mot de passe en clair et zéro chemin personnel dans les journaux ou rapports de diagnostic (`FR-10`, `FR-15`).
   * Historique local désactivé par défaut (`FR-11`).
   * Attestation d'autorisation explicite (`FR-14`) et communication transparente sur les limites du chiffrement (`FR-13`).

---

## Installation & Exécution

```powershell
pip install -r requirements.txt
python pdf_unlocker.py
```

### Mode ligne de commande (CLI)
```powershell
# Vérifier un mot de passe et enregistrer une copie déchiffrée
python pdf_unlocker.py mon_document.pdf --verify 000452 --unlock

# Tester une liste ciblée ou un motif borné
python pdf_unlocker.py mon_document.pdf --candidates "123456,000452,4827??" --unlock
```

### Tests automatisés du PRD (`P0` / `P1`)
```powershell
python tests/test_mvp_prd.py -v
```

### Générer l'exécutable Windows `.exe` + SHA-256
```powershell
python build_windows.py
```

### Créer le package de distribution `.zip`
```powershell
python package_release.py
```

### Créer l'installateur Windows (`Setup.exe` avec Inno Setup)
Si [Inno Setup 6](https://jrsoftware.org/isdl.php) est installé sur votre machine :
```powershell
iscc installer.iss
```
L'installateur sera produit directement dans le dossier `dist/PDF_Unlocker_Setup_v1.0.0.exe`.

---

## Déploiement Web & Distribution Automatique

* **GitHub Actions CI/CD** ([`.github/workflows/build_and_release.yml`](.github/workflows/build_and_release.yml)) :
  - Compilation automatique sur runner Windows dès la création d'un tag Git (ex. `git tag v1.0.0 && git push --tags`).
  - Génération de la Release GitHub avec binaire `.exe`, empreinte `.sha256` et archive `.zip`.
* **Hébergement Landing Page** :
  - **Netlify** : [`netlify.toml`](netlify.toml) préconfiguré (dossier `site/` avec en-têtes de sécurité).
  - **Cloudflare Pages / GitHub Pages** : [`site/_headers`](site/_headers) et workflow [`.github/workflows/deploy_site.yml`](.github/workflows/deploy_site.yml).

---

## Automatisation des Ventes & Délivrance de Licences (Webhooks)

* **Serveur Webhook** ([`server/webhook_server.py`](server/webhook_server.py)) :
  - Écoute les commandes Lemon Squeezy, Stripe et Gumroad avec validation des signatures HMAC.
  - Génère instantanément la clé de licence hors-ligne signée (Pro ou Business).
  - Envoie un e-mail transactionnel professionnel avec la clé et le lien de téléchargement ([`server/email_service.py`](server/email_service.py)).
* **Simulateur de test en direct** :
  ```powershell
  python server/test_webhook.py --tier PRO --email client@domaine.com --name "Jean Dupont"
  ```

