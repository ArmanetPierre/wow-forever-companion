# Plan — Agent compagnon WoW Forever

Objectif : un agent IA qui répond à mes questions sur WoW Forever en s'appuyant sur
des sources fiables **et** sur l'état réel de mon personnage, partageable avec mes amis.

## Constats de départ (12/11/2026)

- WoW Forever = produit Blizzard officiel (`wowf`, client 1.60.1, sorti le 04/11/2026),
  installé dans `/Applications/World of Warcraft/_forever_/`, région EU, client frFR.
- Personnage détecté : `WTF/Account/123456789#1/93/Brannok-Durn`.
- Aucun addon installé pour l'instant. Le système d'addons existe (dossier
  `Interface/AddOns`, SavedVariables Blizzard présents).
- Un addon communautaire (ForeverSVBridge) signale qu'en bêta le client **écrit** les
  SavedVariables à la déconnexion mais ne les **relit** pas. Pour nous ce n'est pas
  bloquant : on a seulement besoin que le jeu écrive les données.

## Architecture : 3 couches

```
┌───────────────────────────── PARTAGEABLE (repo Git) ─────────────────────────────┐
│ 1. Plugin "forever-companion"                                                     │
│    - agent : prompt système (expert WoW Forever, FR, cite ses sources,            │
│      distingue Forever / Classic / Retail)                                        │
│    - skills : quêtes, leveling, métiers, talents, donjons, économie               │
│    - sources.yaml : liste des sites de référence                                  │
│ 2. Addon "ForeverScribe" (Lua, dans Interface/AddOns)                             │
│    - collecte les infos du perso → SavedVariables par personnage                  │
│ 3. Serveur MCP "forever-mcp" (local)                                              │
│    - lit les SavedVariables, expose des outils : get_character, get_quests, …     │
└───────────────────────────────────────────────────────────────────────────────────┘
┌───────────────────────────── PERSONNEL (jamais commité) ──────────────────────────┐
│ perso/config.yaml   chemin WoW, compte, personnage principal                      │
│ perso/<Perso>/profil.md     généré par le MCP à partir de l'addon                 │
│ perso/<Perso>/objectifs.md  rédigé à la main (but, style de jeu, priorités)       │
│ perso/<Perso>/journal.md    historique de progression (auto + notes)              │
└───────────────────────────────────────────────────────────────────────────────────┘
```

Un ami clone le repo, installe l'addon, lance un script `setup` qui crée son propre
`perso/` : il a le même agent, avec ses propres persos.

## L'addon peut-il servir de MCP ?

Pas directement : un addon WoW tourne dans un bac à sable Lua **sans réseau ni accès
fichier**. Sa seule sortie est le fichier SavedVariables, écrit par le jeu au `/reload`,
à la déconnexion ou à la sortie.

Solution propre et conforme aux CGU (même principe que les apps compagnon type
WarcraftLogs/TSM) :

```
Jeu → addon ForeverScribe → /reload → WTF/.../SavedVariables/ForeverScribe.lua
    → forever-mcp (surveille le fichier, parse le Lua) → agent
```

- Rafraîchissement : un `/reload` (ou `/scribe` qui le déclenche) = données à jour.
- Écarté : lecture de pixels/écran ou injection mémoire (zone grise / interdit).
- À explorer : une API web Battle.net pour les profils Forever (inconnue à ce jour).
- Bonus possible : `Logs/` et le journal de combat (`/combatlog`) pour analyser des combats.

### Données collectées par l'addon

| Domaine | Contenu |
|---|---|
| Identité | nom, race, classe, sexe, niveau, XP, ruleset (PvE/PvP/RP/HC), faction |
| Spé / talents | arbre et points dépensés, spé active |
| Métiers | métiers principaux et secondaires, niveau, recettes connues |
| Quêtes | journal de quêtes (objectifs, progression), quêtes terminées si dispo |
| Position | zone, sous-zone, pierre de foyer |
| Équipement | objets portés, sacs, or |
| Réputations | factions et paliers |
| Horodatage | date de capture, pour savoir si les données sont fraîches |

Étape préalable : vérifier en jeu quelles fonctions de l'API existent dans Forever
(`/dump select(4, GetBuildInfo())` pour la version d'interface, puis tests ciblés).

## Sources de connaissances

| Source | Usage |
|---|---|
| Forums Blizzard, catégorie WoW Forever | annonces, bugs, patch notes |
| Warcraft Tavern (section Forever) | guides débutant, classes, leveling |
| warcraft.wiki.gg | API addons |
| Wowhead / sites de base de données | à vérifier : couverture Forever |
| Discords communautaires (EU, FR) | lecture manuelle, pas d'aspiration |

Deux modes : **recherche web en direct** (toujours à jour) et, plus tard, un
**cache local** des pages clés (réponses plus rapides, hors ligne).

Règle du prompt : Forever ajoute du contenu (zones, nouveaux donjons, race Éolide / Skyborne), donc une
info Classic/Retail n'est pas forcément vraie. L'agent signale sa source et son niveau
de certitude.

## Feuille de route

| Phase | Livrable | Valeur |
|---|---|---|
| **P0** | Vérifications en jeu : version d'interface, API disponibles | dé-risque l'addon |
| **P1** | Agent + skills + sources, profil rempli à la main | utilisable tout de suite |
| **P2** | Addon ForeverScribe v1 (identité, spé, métiers, quêtes) | données réelles |
| **P3** | forever-mcp : lecture SavedVariables + génération de `profil.md` | profil auto |
| **P4** | Packaging : repo Git, script `setup`, README pour les amis | partage |
| **P5** | Journal automatique, cache des sources, analyse combat | confort |

## Décisions ouvertes

1. Client IA visé pour les amis : Claude Code (plugin) ou Claude Desktop (MCP seul) ?
   Le MCP marche avec les deux ; les skills/agent sont plus riches dans Claude Code.
2. Langage du MCP : Node/TypeScript (installation `npx` simple) ou Python.
3. Hébergement du repo : GitHub public ou privé partagé.
