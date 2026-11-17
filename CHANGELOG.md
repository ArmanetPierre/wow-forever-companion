# Changelog

## Plugin `forever-companion`

### 0.3.0 — 2026-11-17
- Charte de réponse (`knowledge/format-reponse.md`) : en-tête du perso, verdict d'abord,
  gabarit par type de question, badges et certitude, règle de fraîcheur.
- Formules de calcul sourcées (`knowledge/formules.md`), dont 14 PA = 1 DPS (confirmé en jeu).
- Nouveaux skills `forever-equipement` et `forever-familier` ; les 6 autres appellent
  d'abord les outils MCP.
- Correction : les compétences d'armes existent dans Forever (seul le bonus racial a disparu).

### 0.2.1 — 2026-11-17
- Messages du serveur : « Ctrl+Maj+S ou /sync » au lieu de « /reload ».

### 0.2.0 — 2026-11-17
- Serveur MCP `forever` (Python, bibliothèque standard) : 16 outils (fiche, stats,
  équipement, talents, sorts, quêtes, métiers, sacs, réputations, familier, progression,
  comparaison d'objets et de persos, gestion des persos et des comptes).
- Synchro : `etat.json`, section auto de `profil.md`, journal automatique, un instantané
  par jour, multi-comptes et multi-persos.

### 0.1.0 — 2026-11-12
- Agent `forever-guide`, 6 skills, base de connaissances et sources.

## Addon ForeverScribe

### 1.1.1 — 2026-11-17
- Correctif : à la sortie du jeu, le client renvoie parfois des valeurs vides (PV, XP,
  sacs, argent). L'addon garde alors la capture précédente au lieu de l'écraser.

### 1.1.0 — 2026-11-17
- Synchro en un geste : raccourci (Ctrl+Maj+S par défaut), `/sync`, bouton de minicarte.
  Refusée en combat. Origine de chaque écriture enregistrée.

### 1.0.0 — 2026-11-17
- Capture de 21 domaines (identité, progression, position, stats, équipement, talents,
  sorts, quêtes, métiers, recettes, familier, sacs, banque, argent, réputations,
  monnaies, groupe, effets, collections, réglages Forever).

## Addon ForeverProbe

### 0.1.0 — 2026-11-17
- Sonde de diagnostic : inventaire de l'API et appels de test.
