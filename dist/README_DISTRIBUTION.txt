================================================================================
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

  Get-FileHash -Algorithm SHA256 .\PDF_Unlocker_MVP_1.0.exe

Empreinte officielle attendue :
  978323f622f55aee8390b2634e0db6653fdf6dd133d2557f96486ee623b97f7d  PDF_Unlocker_MVP_1.0.exe

3. DÉMARRAGE RAPIDE
-------------------
Double-cliquez simplement sur 'PDF_Unlocker_MVP_1.0.exe' pour démarrer l'interface graphique.
Aucune installation de dépendance ni droits administrateur ne sont requis.

Mode ligne de commande (CLI) également supporté :
  .\PDF_Unlocker_MVP_1.0.exe --cli --file document.pdf --verify 000452 --output document_ouvert.pdf

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
