# Plan P2-P3 — Contexte joueur maximal et réponses soignées

Statut : **plan, rien n'est développé.** À valider avant de coder.

## 1. Ce qu'on a décidé

| Sujet | Décision |
|---|---|
| Où poser les questions | Dans Claude Code, dans une autre fenêtre (option C). Questions en jeu : bonus pour plus tard |
| Contexte joueur | Le maximum de ce que l'API de Forever expose, capturé par un addon |
| Réponses | Format solide et élégant, qui croise toutes les données disponibles |
| Pas de | Lecture d'écran, touches simulées, injection : interdit par Blizzard |

## 2. Flux de données

```
 EN JEU                    SUR LE MAC                                DANS CLAUDE CODE
┌────────────────┐  /reload  ┌──────────────────────┐            ┌──────────────────────┐
│ ForeverScribe  │ ────────► │ SavedVariables .lua  │            │ agent forever-guide  │
│ (addon Lua)    │  écrit    └──────────┬───────────┘            │  + skills            │
└────────────────┘                      │ lu par                 │                      │
                              ┌─────────▼───────────┐  outils    │  croise :            │
                              │ forever-mcp         │ ─────────► │  · état du perso     │
                              │ (Python, local)     │  MCP       │  · journal, objectifs│
                              │ · parse le Lua      │            │  · knowledge/        │
                              │ · etat.json         │            │  · web (Wowhead…)    │
                              │ · historique        │            └──────────────────────┘
                              │ · profil.md (auto)  │
                              └─────────────────────┘
```

Trois modules indépendants avec un contrat entre eux : le **schéma des données**
(`docs/schema.md`), écrit en premier.

## 3. Étape 0 — Inventaire de l'API Forever (recherche, sans code)

Le client de Forever est basé sur le retail (12.1.5, interface 16001), avec un gameplay
proche de Classic. On ne sait donc pas pour chaque domaine si c'est l'API retail (`C_*`)
ou classique qui répond. Livrable : un tableau domaine → fonction(s) → certitude, à partir
de warcraft.wiki.gg (`Patch_1.60.1/API_changes`, pages `_(Forever)`).

Puis un **addon de sonde** minuscule : il appelle chaque fonction candidate et note ce qui
existe et ce qui renvoie quelque chose. Tu le lances une fois en jeu et on sait exactement
sur quoi construire. Cette étape enlève le plus gros risque du projet.

## 4. Module A — Addon ForeverScribe

### Données capturées

| Priorité | Domaine | Contenu | Quand |
|---|---|---|---|
| **1** | Identité | nom, race, classe, sexe, faction, guilde, ruleset (si accessible) | connexion |
| **1** | Progression | niveau, XP, repos, temps de jeu | niveau / XP |
| **1** | Position | carte, zone, sous-zone, coordonnées, pierre de foyer | changement de zone |
| **1** | Équipement | chaque emplacement : objet, ilvl, qualité, stats, durabilité | changement d'équipement |
| **1** | Stats | primaires, PA et PA à distance, crit, toucher, armure, résistances, DPS mêlée et distance | équipement / buffs |
| **1** | Talents | spé active, points par arbre, talents pris, double spé | changement de talents |
| **1** | Quêtes | journal complet : titre, ID, niveau, zone, objectifs et progression | journal modifié |
| **1** | Métiers | métiers et compétences, niveaux | montée de compétence |
| 2 | Familier (chasseur) | nom, famille, niveau, bonheur, capacités | appel du familier |
| 2 | Sacs | contenu, places libres, munitions/carquois si ça existe | sacs modifiés |
| 2 | Argent, réputations, monnaies | | événement correspondant |
| 2 | Sorts connus | sorts et rangs (savoir quoi aller apprendre chez le maître) | apprentissage |
| 3 | Banque | contenu | seulement quand tu l'ouvres |
| 3 | Recettes | recettes connues | seulement fenêtre de métier ouverte |
| 3 | Quêtes terminées | historique | si l'API le permet |
| 3 | Collections | montures, mascottes, succès | connexion |

### Principes de conception

- **Robuste** : chaque collecteur est isolé ; si une API manque, il note l'erreur
  (`meta.errors`) au lieu de casser l'addon.
- **Léger** : captures déclenchées par événements, regroupées (pas plus d'une toutes les
  quelques secondes), aucun impact en combat.
- **Versionné** : `meta.schemaVersion`, `meta.capturedAt`, version du client.
- **Par personnage** : chaque perso a ses propres données ; un index au niveau du compte.
- Commandes : `/scribe` (capture + résumé), `/scribe status` (ce qui marche ou pas).
- Installation : un script qui relie le dossier du repo à `Interface/AddOns` (macOS ;
  Windows documenté pour les amis).

Limite à retenir : les données ne sortent du jeu qu'au `/reload`, à la déconnexion ou à
la sortie. Réflexe à prendre : un `/reload` avant de poser une question qui dépend de
l'état actuel.

## 5. Module B — forever-mcp (synchro + outils)

**Techno proposée : Python, bibliothèque standard uniquement.** Rien à installer sur un Mac,
facile pour les amis. Il est déclaré dans le plugin et démarre tout seul avec Claude Code.

| Fonction | Détail |
|---|---|
| Parseur | lit le fichier SavedVariables (table Lua) → `perso/<Perso>/etat.json` |
| Profil | régénère uniquement les sections « auto » de `profil.md` ; ne touche jamais à `objectifs.md` ni aux notes manuelles |
| Historique | un instantané par capture dans `perso/<Perso>/historique/` |
| Journal auto | compare deux instantanés et ajoute au journal : niveau pris, quête rendue, nouvel objet, compétence de métier +N, nouvelle zone |
| Fraîcheur | chaque réponse d'outil indique l'âge des données |

Outils exposés à l'agent :

| Outil | Rôle |
|---|---|
| `list_characters` | persos connus et date de dernière capture |
| `get_character` | fiche synthétique (identité, niveau, zone, spé, fraîcheur) |
| `get_stats` / `get_equipment` | stats et équipement détaillés |
| `get_talents` / `get_spells` | build actuel, sorts et rangs connus |
| `get_quests` | journal de quêtes, filtrable par zone |
| `get_professions` / `get_inventory` | métiers, sacs, banque, argent |
| `get_reputations` / `get_pet` | réputations, familier |
| `get_progress` | ce qui a changé depuis une date (alimenté par l'historique) |
| `compare_item` | compare un objet décrit ou donné par ID à l'objet équipé au même emplacement |

## 6. Module C — Réponses : contenu et forme

### Croisement des données (ordre de consultation)

1. **Outils MCP** : état réel et actuel du perso
2. **Fichiers perso** : objectifs, journal, notes
3. **knowledge/** : faits Forever vérifiés et formules
4. **Web** : Wowhead Forever, warcraft.wiki.gg, guides récents, forums
5. Connaissances Classic/Retail, seulement en le signalant

### Charte de réponse (`knowledge/format-reponse.md`)

- **En-tête d'une ligne** : `Brannok · Nain Chasseur 25 · Les Paluns · données d'il y a 3 min`
- **Verdict en premier**, en gras, en une phrase
- **Un gabarit par type de question** : comparaison d'objets (tableau + DPS effectif),
  quête (étapes + `/way`), leveling (plan court), build (ordre des points), métier,
  donjon (préparation, rôle, loot pour ta classe)
- **Badges** [Forever] / [Classic] / [Retail] et certitude : sûr / probable / à vérifier en jeu
- **« Ce que j'ai utilisé »** : quelles données du perso, quelles sources
- **À vérifier en jeu** quand une hypothèse n'est pas confirmée pour Forever
- Sobre : pas de pavé, pas d'emojis décoratifs, chiffres arrondis, tableaux seulement s'ils aident

Exemple de rendu visé :

> `Brannok · Nain Chasseur 25 · Les Paluns · données d'il y a 3 min`
>
> **Prends l'arbalète : environ +20 % de DPS à distance.**
>
> | | Équipé : Fusil à canon double | Arbalète de points dissimulés |
> |---|---|---|
> | DPS arme | 13,0 | 15,2 |
> | Bonus | +3 Agi, +3 For | +12 PA distance |
> | DPS effectif | ≈ 13,4 | **≈ 16,1** |
>
> Le bonus nain aux armes à feu n'existe plus dans Forever [Forever · probable].
>
> **À vérifier en jeu :** l'arbalète en rouge = compétence à apprendre à Forgefer.
>
> *Utilisé : équipement (addon), stats (addon) · Sources : Warcraft Tavern, Icy Veins*

### Compléments

- `knowledge/formules.md` : DPS d'arme, PA → DPS, Agi → PA/crit par classe, XP ;
  chacune marquée [Classic] avec sa certitude pour Forever
- Nouveau skill `forever-equipement` : comparer, améliorer, garder ou vendre

## 7. Ordre de réalisation et critères de fin

| # | Étape | Fini quand |
|---|---|---|
| 0 | Inventaire API + addon de sonde | tableau des API validé en jeu par toi |
| 1 | `docs/schema.md` | schéma figé, version 1 |
| 2 | Addon ForeverScribe (priorité 1) | `/scribe status` sans erreur sur les domaines priorité 1 |
| 3 | Parseur + `etat.json` + `profil.md` auto | ton vrai profil se remplit tout seul |
| 4 | Serveur MCP + outils | l'agent répond « mon niveau ? » via l'outil |
| 5 | Charte de réponse + formules + skill équipement | la question de l'arbalète reproduite avec les vraies données |
| 6 | Addon priorité 2 et 3, historique, journal auto | journal rempli après une session de jeu |
| 7 | Partage (README amis, Windows) | un ami installe tout en suivant le README |

Les étapes 0-1 conditionnent tout. Ensuite, 2 (addon) et 5 (charte) peuvent avancer en
parallèle.

## 8. Plusieurs joueurs et plusieurs personnages

Trois cas à gérer :

| Cas | Exemple | Réponse |
|---|---|---|
| Plusieurs persos | Brannok + un reroll | chaque perso a son dossier et son état ; un perso « actif » par défaut |
| Plusieurs comptes sur un même PC | toi et ton fils sur le même Mac | le jeu sépare déjà les données par compte (`WTF/Account/<compte>`), on garde cette séparation |
| Plusieurs joueurs sur des PC différents | tes amis | chacun installe le repo ; ses données restent chez lui |

**Organisation des fichiers**
```
perso/                         (jamais partagé)
├── config.json                chemin du jeu, utilisateur et perso actifs
└── <Utilisateur>/             ex. Alex
    ├── utilisateur.md         préférences communes à tous ses persos
    └── <Perso>-<Région>/      ex. Brannok-EU
        ├── profil.md  objectifs.md  journal.md
        ├── etat.json
        └── historique/
```

- **Clé unique d'un perso** : nom + région + identifiant interne du jeu (GUID). Forever
  n'a pas de royaumes et les noms sont uniques par région ; le GUID évite toute confusion
  si un perso est renommé ou recréé. La sonde vérifie ce que l'API renvoie.
- **Rattachement compte → utilisateur** : au premier lancement, le script demande à qui
  appartient chaque compte trouvé dans `WTF/Account/` (« Alex », « Lucas »…).
- **Perso actif** : par défaut, le dernier capturé. Tu peux le changer en disant « je joue
  mon mage » ; l'en-tête de chaque réponse affiche toujours le perso utilisé.
- **Outils MCP** : tous prennent un paramètre `perso` facultatif (par défaut le perso
  actif) ; `list_characters` liste tous les persos de tous les utilisateurs ; nouveaux
  outils `set_active_character` et `compare_characters` (ex. qui a le meilleur métier
  pour fabriquer un objet).
- **Addon** : il enregistre déjà ses données perso par perso, avec un index des persos
  du compte.

## 9. Compatibilité macOS / Windows / Linux

| Élément | macOS | Windows | Linux |
|---|---|---|---|
| Addon (Lua) | identique | identique | identique (jeu via Wine/Lutris) |
| Dossier du jeu | `/Applications/World of Warcraft/_forever_` | `C:\Program Files (x86)\World of Warcraft\_forever_` | dans le préfixe Wine, ex. `~/Games/battlenet/drive_c/Program Files (x86)/…` |
| Python | préinstallé (`python3`) | **à installer** (python.org ou `winget install Python.Python.3.12`) | préinstallé (`python3`) |
| Installation de l'addon | lien symbolique | jonction (`mklink /J`, sans droits admin) ou copie | lien symbolique |
| Script d'installation | `install.sh` | `install.ps1` | `install.sh` |
| Claude Code | oui | oui | oui |

Règles de code pour que ça marche partout :
- chemins via `pathlib`, jamais de `/` en dur ; chemin du jeu détecté puis confirmé par
  l'utilisateur et stocké dans `perso/config.json` ;
- fichiers lus en UTF-8 et fins de ligne Windows (CRLF) acceptées par le parseur ;
- surveillance du fichier par simple vérification périodique (pas d'outil propre à un OS) ;
- le script d'installation trouve la bonne commande Python (`python3`, `python` ou `py`)
  et l'écrit dans la configuration du serveur MCP.

Linux : Blizzard ne supporte pas officiellement le jeu sous Wine, mais il y fonctionne et
l'addon n'y voit aucune différence.

## 10. Décisions à prendre

1. **Python** pour le serveur MCP (rien à installer) : d'accord ?
2. **Journal automatique** : activé par défaut, ou seulement sur demande ?
3. **Historique** : garder tous les instantanés, ou seulement les N derniers jours ?
4. **Amis sur Windows** : à prévoir dès maintenant, ou plus tard ?
5. **Données sensibles** : rien de sensible a priori (pas d'identifiants), mais le dossier
   `perso/` reste hors du partage. OK ?
