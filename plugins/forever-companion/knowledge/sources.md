# Sources WoW Forever — liste vérifiée

> Recherche effectuée le 12/11/2026 (jeu sorti le 04/11/2026, client 1.60.1, code produit `wowf`).
> Légende : **VÉRIFIÉ** = page ouverte et lue ce jour · **INDEXÉ** = URL vue dans les résultats de recherche mais page non lisible (403 ou non ouverte) · **SUPPOSÉ** = déduit, pas confirmé.
> Attention : Warcraft Tavern, Icy Veins et PlayNews renvoient une erreur 403 aux outils de lecture automatique. Il faut donc s'appuyer sur leurs extraits de recherche ou sur une autre source.

## Point de vocabulaire important (FR / EN)

- **Skyborne n'est pas le nom de donjons** : c'est la **nouvelle race jouable** (FR officiel : **Éolides**), avec sa zone de départ **Zephras Isle** (FR : **île de Zéphras**, niveaux 1-12). Les packs payants s'appellent « Skyborne Heroic/Epic Pack » (FR : « pack héroïque des Éolides »). Sources : [Blizzard FR](https://news.blizzard.com/fr-fr/article/24315643), [warcraft.wiki.gg](https://warcraft.wiki.gg/wiki/Forever).
- Le nom de code interne (API, TOC) est **Camelot**. L'alias `forever` est accepté.
- Ruleset Hardcore = **« Extrême »** dans le client français.

---

## 1. Sources officielles Blizzard

| Source | URL | Contenu | Fiabilité | Langue | Statut |
|---|---|---|---|---|---|
| Blizzard News (FR) — annonce/lancement | https://news.blizzard.com/fr-fr/article/24315643 | Races, nouvelles combinaisons race/classe, 9 donjons (noms FR), systèmes, rulesets, accès | Officielle, la plus fiable | FR | VÉRIFIÉ |
| Blizzard News (FR) — guide débutant | https://news.blizzard.com/fr-fr/article/24315280 | Métiers (2 principaux + 3 secondaires), campements, rulesets, préréglages Classique/Amélioré, noms FR des zones | Officielle | FR | VÉRIFIÉ |
| Blizzard News — « Carve a New Path » (miroir Wowhead blue tracker EU) | https://www.wowhead.com/forever/blue-tracker/news/eu/24302093 (FR : https://news.blizzard.com/fr-fr/article/24302093) | Éditions (Heroic, Epic, Collection, Collector), accès inclus dans l'abonnement, heure de sortie | Officielle (repost) | EN/FR | VÉRIFIÉ (miroir EN) |
| Blizzard News — Deep Dive Panel Recap | https://news.blizzard.com/en-us/article/24303313 | Rulesets, règles de groupe, refonte des raciaux, structure des talents (paliers 11/16/21/31), changements Paladin | Officielle | EN | VÉRIFIÉ |
| Autres articles Blizzard FR | https://news.blizzard.com/fr-fr/article/24303862 · …/24304160/beta · …/24301508 · …/24303313 · …/24315820 | Récapitulatifs, bêta, etc. | Officielle | FR | INDEXÉ |
| Site officiel | https://worldofwarcraft.blizzard.com/en-us/forever | Page vitrine. Le contenu se charge en JS et n'est pas lisible par l'outil, seul le titre ressort | Officielle | EN (fr-fr probable) | VÉRIFIÉ (contenu vide à la lecture) |
| X officiel | https://x.com/warcraft | Annonces rapides, incidents | Officielle | EN | SUPPOSÉ (lien trouvé sur le site officiel) |

Modèles de recherche :
- `site:news.blizzard.com/fr-fr "Forever" <terme>`
- `site:news.blizzard.com "World of Warcraft: Forever" correctifs` (notes de correctifs, hotfixes)

## 2. Forums Blizzard

| Forum | URL | Contenu | Statut |
|---|---|---|---|
| US — catégorie WoW: Forever | https://us.forums.blizzard.com/en/wow/c/wow-forever/346 | Très actif. Sous-forums General Discussion (https://us.forums.blizzard.com/en/wow/c/wow-forever/347), Bug Report, Community Connections. Posts « bleus » (p. ex. Kaivax, « PvP Faction Balance Updates – November 10 ») | VÉRIFIÉ |
| EU anglais — WoW: Forever | https://eu.forums.blizzard.com/en/wow/c/wow-forever/359 | Catégorie quasi vide (1 sujet le 12/11) | VÉRIFIÉ |
| EU français — World of Warcraft Forever | https://eu.forums.blizzard.com/fr/wow/c/world-of-warcraft-forever/213 | La catégorie existe mais compte 0 sujet le 12/11 | VÉRIFIÉ |

Fiabilité : les posts de Blizzard (Community Managers) sont fiables. Les posts de joueurs reflètent l'opinion et les bugs constatés, ils sont utiles pour savoir si un bug est connu.
Modèles de recherche : `site:us.forums.blizzard.com/en/wow/c/wow-forever <terme>` ; `site:us.forums.blizzard.com "Forever" Kaivax <terme>` (pour les posts bleus).

## 3. Bases de données

| Source | URL / préfixe | Contenu | Statut |
|---|---|---|---|
| **Wowhead Forever** | `https://www.wowhead.com/forever` ; FR : `https://www.wowhead.com/forever/fr` | Section dédiée « WoW Forever News and Guides » : actualités (« World of Warcraft: Forever is Live! » 4 nov., « Darkmoon Faire is Live! » 9 nov.), blue tracker, base d'objets (`/forever/item-sets`, `/forever/fr/item-sets` en français). Le Wowhead Client gère Forever depuis le 17/09/2026 | VÉRIFIÉ (accueil + item-sets FR). Motifs `/forever/item=ID`, `/forever/quest=ID`, `/forever/npc=ID` : SUPPOSÉS (même schéma que `/classic/`), non confirmés |
| warcraft.wiki.gg — catégorie objets Forever | https://warcraft.wiki.gg/wiki/Category:Forever_items | Objets propres à Forever | INDEXÉ |
| WarcraftDB / Lexicon Client (Warcraft Tavern) | https://www.warcrafttavern.com/forever/news/help-build-a-better-database-for-wow-forever-with-the-lexicon-client/ | Base communautaire alimentée par un client de collecte | INDEXÉ |
| Rankedboost, Metaforge | https://rankedboost.com/world-of-warcraft/forever/items/ · https://metaforge.app/wow-forever/database/items | Bases d'objets tierces (fiabilité moindre) | INDEXÉ |

Modèles de recherche : `site:wowhead.com/forever <nom de l'objet/quête/PNJ>` ; `site:wowhead.com/forever/fr <nom français>`.
Ne pas confondre avec `wowhead.com/classic` (Classic Era) : les données diffèrent (nouveaux talents, nouvelles quêtes).

## 4. Wikis

| Source | URL | Contenu | Statut |
|---|---|---|---|
| **warcraft.wiki.gg** — page principale | https://warcraft.wiki.gg/wiki/Forever (alias `World_of_Warcraft:_Forever`, `Patch_1.60`, `Patch_1.60.1`) | Très complet et à jour (modifié le 12/11/2026) : calendrier, races, donjons avec niveaux, raids, systèmes, rulesets, éditions, références | VÉRIFIÉ, très fiable |
| warcraft.wiki.gg — capacités Chasseur | https://warcraft.wiki.gg/wiki/Hunter_abilities_(Forever) | Capacités par niveau et talents des 3 arbres | VÉRIFIÉ |
| warcraft.wiki.gg — pages `(Forever)` | p. ex. https://warcraft.wiki.gg/wiki/Lone_Wolf_(Forever), https://warcraft.wiki.gg/wiki/Warlock_abilities_(Forever) | Pages de sorts et de talents propres à Forever, suffixées `_(Forever)` | INDEXÉ |
| Wowpedia (Fandom) | — | Les pages d'avant octobre 2023 ont migré vers warcraft.wiki.gg. Pas de contenu Forever trouvé | SUPPOSÉ obsolète pour Forever |

Modèle : `site:warcraft.wiki.gg "(Forever)" <terme>` ou l'URL directe `https://warcraft.wiki.gg/wiki/<Nom>_(Forever)`.

## 5. Sites de guides (EN)

| Source | URL | Contenu | Statut |
|---|---|---|---|
| **Warcraft Tavern** | https://www.warcrafttavern.com/forever/ ; guides : `/forever/guides/…` (p. ex. `/forever/guides/hunter/`, `/forever/guides/hunter-leveling/`, `/forever/guides/overview/`) ; news : `/forever/news/` | Guides de classe, leveling, actualités, roadmap. Spécialiste Classic, fiable | INDEXÉ (403 à la lecture) |
| **Icy Veins** | `https://www.icy-veins.com/wow-forever/…` (p. ex. `/wow-forever/beast-mastery-hunter-leveling`, `/wow-forever/marksmanship-hunter-leveling`, `/wow-forever/survival-hunter-leveling`, `/wow-forever/roadmap`, `/wow-forever/general-info`) | Guides de leveling par spé, roadmap | INDEXÉ (403) |
| **Method.gg** | `https://www.method.gg/wow-forever/…` | Guide Chasseur leveling et talents (Celz, mis à jour le 10/11/2026) | VÉRIFIÉ |
| Mobalytics | `https://mobalytics.gg/wow-forever/…` (classes, tier lists, guides de leveling) | Nombreux guides, dont certains communautaires (fiabilité variable) | INDEXÉ |
| wow.gg | `https://wow.gg/guides/…` ; FR : `https://wow.gg/fr/guides/wow-forever-…` | Guides de spé (Fouren), traduits en FR | VÉRIFIÉ (guide Survie FR) |
| Gfinity (UI/addons, roadmap) | https://www.gfinityesports.com/article/world-of-warcraft-forever-ui-addons-setup-guide · …/world-of-warcraft-forever-roadmap-guide | Addons, roadmap | INDEXÉ |

Modèles : `site:warcrafttavern.com/forever <terme>` ; `site:icy-veins.com/wow-forever <terme>` ; `site:method.gg/wow-forever <terme>`.
Attention : beaucoup de guides datent de la **bêta (plafonnée au niveau 30)**. Il faut vérifier la date de mise à jour (après le 04/11/2026).

## 6. Sites francophones

| Source | URL | Contenu | Statut |
|---|---|---|---|
| Blizzard News FR | voir §1 | Terminologie officielle FR | VÉRIFIÉ |
| Wowhead FR (section Forever) | https://www.wowhead.com/forever/fr | Base de données en français | VÉRIFIÉ (page item-sets FR) |
| wow.gg FR | https://wow.gg/fr/guides/wow-forever-survival-hunter (et `-marksmanship-hunter`, `-beast-mastery-hunter-beta`) | Guides de spé Chasseur en FR | VÉRIFIÉ (Survie) |
| PlayNews | https://www.playnews.gg/guides/chasseur-wow-forever-build-survie-ou-precision-quels-talents-choisir-en-solo · …/familier-chasseur-wow-forever-comment-l-apprivoiser-et-le-nourrir · …/serveur-francais-wow-forever-… | Guides FR (Chasseur, familier, joueurs FR) | INDEXÉ (403) |
| Kami-Labs | https://kami-labs.fr/wow-forever/build-chasseur-maitrise-des-betes-wow-forever/ | Builds Chasseur FR | INDEXÉ |
| Gamewave | https://gamewave.fr/world-of-warcraft-forever/actualites/ | Actus FR | INDEXÉ |
| Seemeta (calculateur de talents FR) | https://seemeta.com/fr/wow-forever/talent-calculator/hunter | Calculateur de talents Chasseur | INDEXÉ |
| **JudgeHype** | https://worldofwarcraft.judgehype.com/ | Aucun contenu Forever trouvé au 12/11 (seul un ancien guide Chasseur retail est ressorti) | SUPPOSÉ non couvert |
| **Mamytwink** | — | Aucun résultat Forever trouvé | SUPPOSÉ non couvert |

Modèles : `"WoW Forever" chasseur <terme>` ; `site:wow.gg/fr "forever" <terme>`.

## 7. Communautés (Reddit, Discord)

- **Reddit** : aucun subreddit dédié (r/WoWForever) n'a été trouvé. Le site officiel renvoie vers **r/wow** (https://www.reddit.com/r/wow). Le sujet est aussi traité sur **r/classicwow**. Statut : SUPPOSÉ, non ouvert.
- **Discord** : aucun Discord Forever officiel ou FR n'a été vérifié. Statut : non confirmé.
- Joueurs francophones : il n'y a **pas de serveur français**, puisque le jeu fonctionne avec des rulesets à la place des royaumes. Selon PlayNews (extrait de recherche, non ouvert), on peut régler la « Langue en ligne préférée » en jeu.

## 8. API addons

| Élément | Valeur | Source | Statut |
|---|---|---|---|
| Version d'interface (TOC) | **16001** (patch 1.60.1) | https://warcraft.wiki.gg/wiki/Patch_1.60.1/API_changes | VÉRIFIÉ |
| Base de code | Branche Mainline, basée sur **12.1.5** (build 69952). Forever (Camelot) et Midnight (Standard) sont deux types de jeu de la même famille | idem | VÉRIFIÉ |
| Project ID | `WOW_PROJECT_CAMELOT = 18`. Test : `WOW_PROJECT_ID == WOW_PROJECT_CAMELOT`, ou interface `> 16000 and < 20000` | idem | VÉRIFIÉ |
| Suffixe TOC | `MonAddon_Forever.toc` (alias de `_Camelot`) ; directives `## AllowLoadGameType: forever`, `## ExcludeLoadGameType: standard, classic` | idem | VÉRIFIÉ |
| Restrictions | Les restrictions d'addons et « secrets » de Midnight s'appliquent aussi. Les GUID de créatures sont obfusqués. `require` est renommé `import` en Lua. `C_PvP.IsWarModeFeatureEnabled` renvoie false | idem | VÉRIFIÉ |
| Builds bêta | 70009 (23/09), 70170 (01/10), 70205 (02/10), 70291 (07/10, Beta 4), 70425 (Beta 5, 16/10). Le build de lancement n'a pas été trouvé | idem | VÉRIFIÉ / build de sortie non confirmé |
| Compatibilité | Les addons Classic Era ne se chargent pas. Les addons Midnight se portent facilement. Forever recharge les addons et raccourcis du retail | Gfinity (indexé) ; Warcraft Tavern https://www.warcrafttavern.com/forever/news/wow-forever-loads-your-retail-addons-keybinds/ (indexé) | INDEXÉ |
| Notes détaillées | https://warcraft.wiki.gg/wiki/Patch_1.60.1/API_changes/notes | — | INDEXÉ |
| Doc générale | https://warcraft.wiki.gg/wiki/TOC_format · https://warcraft.wiki.gg/wiki/Getting_the_current_interface_number | — | INDEXÉ |
| Addons Forever | CurseForge (p. ex. ClassicUI Forever, QuietUI, XE QoL Forever), Wago | — | INDEXÉ |

## Top 5 fiabilité

1. Blizzard News (FR/EN) : officiel et terminologie FR.
2. warcraft.wiki.gg (`/wiki/Forever` + pages `_(Forever)`) : le plus complet et à jour.
3. Forums Blizzard US, catégorie 346 : posts bleus, bugs connus.
4. Wowhead `/forever` (et `/forever/fr`) : base de données et actualités.
5. Warcraft Tavern `/forever/` et Icy Veins `/wow-forever/` : guides de classe et de leveling (à lire hors outil automatique, 403).
