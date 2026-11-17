# WoW Forever Companion

Un compagnon IA pour **World of Warcraft: Forever**, dans
[Claude Code](https://claude.com/claude-code). Tu lui poses tes questions dans une fenêtre
à côté du jeu ; il répond en français en croisant **l'état réel de ton personnage**
(capturé en jeu par un addon) avec des sources fiables sur Forever.

> *English summary below.*

```
Brannok · Nain Chasseur 25 · Les Paluns · données d'il y a 4 min

Oui, mais pas tout de suite : environ +2,4 DPS (+5,5 %) une fois ta compétence
Arbalètes montée.

|                               | Fusil à canon double | Arbalète de points dissimulés |
|-------------------------------|----------------------|-------------------------------|
| DPS de l'arme                 | 13,3                 | 15,2                          |
| Bonus                         | +3 Agi, +3 For       | +12 PA à distance             |
| DPS à distance (coups blancs) | 43,1                 | ≈ 45,5                        |

- Ta compétence Arbalètes est à 1/125 : au début, beaucoup de tirs vont rater.

Basé sur : équipement et stats (addon), compare_item · Certitude : probable
```

## Ce que contient le projet

| Élément | Rôle |
|---|---|
| Addon **ForeverScribe** | capture en jeu l'état de ton perso : identité, XP, position, stats, équipement, talents, sorts, quêtes, métiers et recettes, familier, sacs, banque, or, réputations… |
| Plugin Claude Code **forever-companion** | l'agent `forever-guide`, 8 skills, une base de connaissances Forever et le serveur MCP |
| Serveur MCP **forever** | lit les captures de l'addon et les donne à l'agent (20 outils) ; tient ton profil et ton journal à jour tout seul ; garde la mémoire de recherche |

Skills : `forever-quetes`, `forever-leveling`, `forever-metiers`, `forever-talents`,
`forever-donjons`, `forever-equipement`, `forever-familier`, `forever-profil`.

## Prérequis

- World of Warcraft: Forever
- [Claude Code](https://claude.com/claude-code)
- Python 3.9 ou plus (déjà présent sur macOS et Linux ; à installer sur Windows)

## Installation

**1. L'addon**

```bash
git clone https://github.com/ArmanetPierre/wow-forever-companion.git
cd wow-forever-companion
addon/install.sh                 # macOS / Linux (détecte le dossier du jeu)
```

Windows (PowerShell) : `powershell -ExecutionPolicy Bypass -File addon\install.ps1`.
Dossier du jeu non trouvé : ajoute `--wow-path "/chemin/vers/World of Warcraft/_forever_"`
(`-WowPath` sous Windows). Sans script : copie `addon/ForeverScribe` dans
`World of Warcraft/_forever_/Interface/AddOns/`.

Puis **quitte complètement le jeu et relance-le**, coche ForeverScribe dans la liste des
AddOns (et « Charger les addons obsolètes » si besoin).

**2. Le plugin**, dans Claude Code :

```
/plugin marketplace add ArmanetPierre/wow-forever-companion
/plugin install forever-companion@wow-forever-companion
```

**3. Ton dossier de joueur** : c'est là que vivent tes données, en dehors du projet.

```bash
mkdir -p ~/WowForever && cd ~/WowForever && claude
```

Lance toujours Claude Code depuis ce dossier pour parler à ton compagnon. Copie-y le modèle
[`perso.example/CLAUDE.md`](perso.example/CLAUDE.md) (renomme-le `CLAUDE.md` et remplis
ton prénom et ton perso) : il dit à Claude de charger tous les outils `forever` en un seul
appel en début de session (`ToolSearch` avec la requête `+forever`), de consulter la
mémoire de recherche avant le web et de suivre la charte de réponse.

## Utilisation

1. En jeu, synchronise : **Ctrl+Maj+S**, `/sync` ou le bouton parchemin près de la
   minicarte (court écran de chargement ; refusé en combat). La déconnexion synchronise
   aussi toute seule. Si le raccourci ne répond pas : `/scribe touche`.
2. Dans Claude Code, pose ta question :
   - « Je fais quoi maintenant ? »
   - « Quelles quêtes je peux rendre ici ? »
   - « Je prends cette arbalète : 24-37, 15,2 DPS, +12 PA à distance ? »
   - « Mon familier est malheureux, je fais quoi ? »
   - « Comment monter mon Travail du cuir de 106 à 150 ? »
   - « Évalue mon stuff » (récompenses de quête comprises)

Chaque réponse commence par ton perso et l'âge des données, donne le verdict d'abord,
puis les détails, la provenance ([Forever], [Classic], [Retail]) et la certitude. Si ta
question dépend de ton état actuel et que les données sont anciennes, l'agent te propose
de synchroniser.

Principaux outils de l'agent : `get_overview` (vue d'ensemble en un appel),
`get_quest_rewards` (récompenses des quêtes du journal classées pour ton perso : maîtrise
d'armure et d'arme, gain estimé, quêtes à rendre qui donnent une amélioration),
`compare_item`, `get_equipment`, `get_inventory`, `get_quests`, `get_talents`,
`get_professions`, `get_pet`, `get_progress`…

**Mémoire de recherche.** Quand l'agent a dû chercher longtemps (« y a-t-il des casques à
mon niveau ? »), il enregistre la réponse avec `save_knowledge` dans
`~/WowForever/connaissances/` : un fichier Markdown par sujet, daté, avec ses sources et sa
certitude. À la question suivante, `search_knowledge` répond en un appel. Ce sont de
simples fichiers texte : relis-les, corrige-les ou supprime-les librement.

Autres commandes en jeu : `/scribe` (capture + résumé), `/scribe status` (état de chaque
domaine), `/scribe bouton` (afficher/masquer le bouton), `/scribe help`.

## Tes données

- **Tout reste sur ton ordinateur.** L'addon écrit un fichier du jeu ; le serveur MCP le
  lit localement. Les informations ne sortent que vers ta propre session Claude, quand tu
  poses une question.
- Aucun identifiant de connexion n'est lu ni stocké.
- Emplacement du dossier de données, dans cet ordre : variable `FOREVER_DATA_DIR`, sinon
  `perso/` dans le dossier où tu lances Claude Code, sinon `~/WowForever/perso`.

```
~/WowForever/
├── CLAUDE.md                    consignes du compagnon (modèle : perso.example/CLAUDE.md)
├── connaissances/               mémoire de recherche (FOREVER_KNOWLEDGE_DIR pour la déplacer)
└── perso/
    ├── config.json              dossier du jeu, comptes, perso actif
    └── <Prénom>/<Perso>-<Région>/
        ├── profil.md            section auto + tes notes
        ├── objectifs.md         tes objectifs (à toi de l'écrire)
        ├── journal.md           tes notes + journal automatique
        ├── etat.json            dernière capture
        └── historique/          un instantané par jour
```

## Plusieurs persos, plusieurs joueurs

- Tous tes persos sont suivis : l'agent répond pour le dernier joué, ou dis « je joue mon
  mage ». Connecte chaque perso une fois avec l'addon actif.
- Plusieurs comptes WoW sur le même ordinateur : chaque compte est rattaché à un prénom
  (l'agent te le demande).
- Tes amis installent le projet chez eux : leurs données restent chez eux.

## Windows et Linux

- **Windows** : installe Python (Microsoft Store, qui fournit `python3`). Avec
  l'installeur de python.org (`python`/`py`), déclare le serveur à la main :
  `claude mcp add forever -- py "<chemin du plugin>\mcp\server.py"`.
- **Linux** : le jeu tourne via Wine/Lutris ; l'addon fonctionne normalement. Si le
  dossier du jeu n'est pas trouvé :
  `python3 plugins/forever-companion/mcp/sync.py --wow "/chemin/vers/World of Warcraft"`.

## Dépannage

| Problème | Solution |
|---|---|
| L'addon n'apparaît pas | quitte et relance le jeu (un `/reload` ne charge pas un nouvel addon) ; sinon réinstalle avec `--copy` |
| « Aucun perso connu » | connecte ton perso, synchronise (Ctrl+Maj+S), vérifie que tu lances Claude Code depuis `~/WowForever` |
| Ctrl+Maj+S ne fait rien | `/scribe touche`, ou Options → Raccourcis → AddOns → ForeverScribe |
| Recettes ou banque vides | ouvre une fois la fenêtre du métier ou la banque, puis synchronise |
| Dossier du jeu introuvable | `sync.py --wow "<dossier du jeu>"` (il est ensuite retenu) |
| « Récompenses de quête inconnues » | mets l'addon à jour (1.2 ou plus), relance le jeu une fois, puis synchronise |

## Feuille de route

- Questions posées directement en jeu (expérimental)
- Cache local des sources de référence
- Analyse de combat (compteur de dégâts intégré à Forever)

Banc d'évaluation du compagnon (scénarios rejouables, critères, budgets) :
[docs/evals/](docs/evals/). Détails de conception : [docs/conception/](docs/conception/), format des données :
[docs/schema.md](docs/schema.md), API vérifiée : [docs/api-inventaire.md](docs/api-inventaire.md).
Pour contribuer : [CONTRIBUTING.md](CONTRIBUTING.md).

## English summary

An AI companion for **World of Warcraft: Forever**, running in Claude Code. The
**ForeverScribe** addon captures your character's state in game (stats, gear, talents,
quests, professions, pet, bags…); press **Ctrl+Shift+S** (or `/sync`) to write it to disk.
The **forever-companion** plugin's local MCP server reads it, and the `forever-guide`
agent answers your questions (in French) by combining your real data with trusted
Forever sources. Everything stays on your machine.

Install: run `addon/install.sh` (or `install.ps1` on Windows), then in Claude Code
`/plugin marketplace add ArmanetPierre/wow-forever-companion` and
`/plugin install forever-companion@wow-forever-companion`, and start `claude` from
`~/WowForever`. Requires Python 3.9+.

## Licence

[MIT](LICENSE) © 2026 Pierre Armanet. Projet de fan, non affilié à Blizzard
Entertainment. World of Warcraft est une marque de Blizzard Entertainment.
