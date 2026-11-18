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
| Blizzard News — Raid Overview | https://news.blizzard.com/en-gb/article/24303009 | Raids du 9/12 (tailles, niveau 60), harmonisation d'Onyxia étape par étape par faction | Officielle | EN | VÉRIFIÉ (18/11/2026) |
| Blizzard News — Choose Your Ruleset | https://news.blizzard.com/article/24302070/ | Rulesets, groupe et champs de bataille entre rulesets, une faction en JcJ, Hardcore et transfert après la mort | Officielle | EN | VÉRIFIÉ (18/11/2026) |
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
| **QuestieDB (Forever)** | https://github.com/Questie/QuestieDB (`data/Forever/`, `l10n/Forever/`) | Base communautaire de l'addon Questie : quêtes (donneur, receveur, niveaux, races, objectifs, prérequis, suites), PNJ et objets avec positions, sources des objets de quête, noms traduits. **Intégrée à la base locale** (outils `quests`, `npc`, `search`, badge `[Forever · QuestieDB]`), téléchargée chez le joueur, jamais redistribuée (licence non déclarée, Questie sous GPLv3). Couverture partielle des quêtes ajoutées par Forever ; une quête refaite peut différer | VÉRIFIÉ (révision fixée dans `gamedata/questie.py`) |
| **Wowhead Forever — infobulle à la demande** | `https://nether.wowhead.com/tooltip/<npc\|object\|quest>/<id>?dataEnv=16` | Nom, zone et points d'un PNJ ou d'un objet du monde ; nom, niveau et objectif d'une quête. Interrogée par le serveur **une id à la fois**, seulement quand aucune source locale ne répond (3 requêtes au plus par appel, cache local, `web_lookup: false` pour couper). Badge `[Wowhead Forever]` | VÉRIFIÉ (réponses JSON avec `dataEnv=16`) |
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
| warcraft.wiki.gg — Salle des Thanes | https://warcraft.wiki.gg/wiki/Hall_of_Thanes_(instance), https://warcraft.wiki.gg/wiki/Farsen's_Watch | Entrée, chaîne d'accès Alliance (Farsen's Watch → Old Ironforge Incursion), quêtes du donjon ; donneurs non listés | VÉRIFIÉ (18/11/2026) |
| warcraft.wiki.gg — pages `(Forever)` | p. ex. https://warcraft.wiki.gg/wiki/Lone_Wolf_(Forever), https://warcraft.wiki.gg/wiki/Warlock_abilities_(Forever) | Pages de sorts et de talents propres à Forever, suffixées `_(Forever)` | INDEXÉ |
| Wowpedia (Fandom) | — | Les pages d'avant octobre 2023 ont migré vers warcraft.wiki.gg. Pas de contenu Forever trouvé | SUPPOSÉ obsolète pour Forever |

Modèle : `site:warcraft.wiki.gg "(Forever)" <terme>` ou l'URL directe `https://warcraft.wiki.gg/wiki/<Nom>_(Forever)`.

## 5. Sites de guides (EN)

| Source | URL | Contenu | Statut |
|---|---|---|---|
| **Warcraft Tavern** | https://www.warcrafttavern.com/forever/ ; guides : `/forever/guides/…` (p. ex. `/forever/guides/hunter/`, `/forever/guides/hunter-leveling/`, `/forever/guides/overview/`) ; news : `/forever/news/` | Guides de classe, leveling, actualités, roadmap. Spécialiste Classic, fiable | INDEXÉ (403 à la lecture) |
| **Icy Veins** | `https://www.icy-veins.com/wow-forever/…` (p. ex. `/wow-forever/beast-mastery-hunter-leveling`, `/wow-forever/marksmanship-hunter-leveling`, `/wow-forever/survival-hunter-leveling`, `/wow-forever/roadmap`, `/wow-forever/general-info`) | Guides de leveling par spé, roadmap | INDEXÉ (403) |
| **Method.gg** | `https://www.method.gg/wow-forever/…` | Guide Chasseur leveling et talents (Celz, mis à jour le 10/11/2026) | VÉRIFIÉ |
| Method.gg — XP des donjons | https://www.method.gg/wow-forever/wow-forever-dungeon-xp-explained-and-all-dungeons-by-level | Historique des réglages d'XP de donjon (bêta → correctif du 9/11), règle d'écart de niveau, niveaux des 9 donjons | VÉRIFIÉ (article du 14/11/2026) |
| Mobalytics | `https://mobalytics.gg/wow-forever/…` (classes, tier lists, guides de leveling) | Nombreux guides, dont certains communautaires (fiabilité variable) | INDEXÉ |
| wow.gg | `https://wow.gg/guides/…` ; FR : `https://wow.gg/fr/guides/wow-forever-…` | Guides de spé (Fouren), traduits en FR | VÉRIFIÉ (guide Survie FR) |
| Gfinity (UI/addons, roadmap) | https://www.gfinityesports.com/article/world-of-warcraft-forever-ui-addons-setup-guide · …/world-of-warcraft-forever-roadmap-guide | Addons, roadmap | INDEXÉ |
| Icy Veins — correctifs du 11/11 | https://www.icy-veins.com/wow-forever/news/dont-vendor-gear-you-might-want-back-item-restoration-disabled/ | Restauration d'objets désactivée (bug critique), sans date de retour | INDEXÉ (403 ; contenu recoupé par Warcraft Tavern, Gamerfuzion, AccountShark, 18/11/2026) |
| Icy Veins — transports | https://www.icy-veins.com/wow-forever/news/boats-and-zeppelins-getting-lost-portals-added-phasing-issues-showing-very-few-players-wow-forever-hotfixes/ | Bateaux et zeppelins perdus, portails temporaires près des quais (citation Blizzard) | INDEXÉ (semaine du lancement) |
| Icy Veins / TechRadar — pierres d'invocation | https://www.icy-veins.com/wow-forever/news/wow-forever-devs-explain-why-summoning-stones-wont-be-added/ · https://www.techradar.com/gaming/blizzard-explains-why-wow-forever-wont-have-summoning-stones-says-easy-quick-access-to-teleports-shrink-the-world-and-easily-erodes-its-core-design-pillars | Pas de pierres d'invocation, choix de design expliqué par Blizzard | INDEXÉ (18/11/2026) |
| Destructoid / Timesaver — layering | https://www.destructoid.com/how-to-change-layers-in-wow-forever-after-the-layer-size-change/ · https://timesaver.gg/blog/wow-forever-layering-sharding-explained | Couches, invitation de couche, différences avec Classic | INDEXÉ (guides) |
| Verrou de faction JcJ | https://eu.forums.blizzard.com/en/wow/t/639733 · https://games.gg/world-of-warcraft/guides/wow-forever-this-faction-is-currently-unavailable-what-it-means/ · https://massivelyop.com/2026/11/14/world-of-warcraft-forever-signals-that-its-not-letting-up-on-faction-locks-on-pvp-rulesets-any-time-soon/ | Verrou d'équilibrage temporaire (Horde au lancement), distinct de la règle « une faction en JcJ » | INDEXÉ (réponse du staff EU, 14/11/2026) |
| Warcraft Tavern — problèmes connus | https://www.warcrafttavern.com/forever/news/pvp-vendors-unavailable-other-known-issues-in-wow-forever/ | Marchands JcJ indisponibles, Vorsha, parrainage | INDEXÉ (403, semaine du lancement) |
| Héritage (Legacy) | https://www.icy-veins.com/wow-forever/news/how-does-the-legacy-system-work-in-wow-forever/ · https://www.wowhead.com/news=383067 · https://www.warcrafttavern.com/forever/news/legacy-rewards-will-be-separate-on-the-wow-forever-hardcore-ruleset/ | Plafond de 16 points par perso, piste de récompenses, sens unique Hardcore → autres rulesets | INDEXÉ (paliers divergents) |
| Blizzard — Meet the New Skyborne | https://worldofwarcraft.blizzard.com/news/24302071/ | Raciaux des Éolides (Walk on Air, Wind Blessed…) | INDEXÉ (officiel ; temps de recharge divergents dans les guides) |
| Prix de respé | https://www.icy-veins.com/wow-forever/news/will-blizzard-change-the-respec-cost-before-2026-is-over/ · https://lfcarry.com/guides/wow-forever-respec-cost | 1 po la première, jusqu'à 50 po, baisse avec le temps | INDEXÉ (sources divergentes, 11/11/2026) |
| RankedBoost — bonus de métiers | https://rankedboost.com/world-of-warcraft/forever/professions/bonuses/ | Objets de campement par métier (20/140/300), pas de bonus passif, potions de soins en Secourisme | VÉRIFIÉ (page lue, vérifiée le 11/11/2026 par le site) |
| PCGames — récompenses de quête de donjon | https://www.pcgames.de/World-of-Warcraft-Spiel-42971/News/WoW-Forever-Dungeon-Quest-Item-Nerfs-1556296/ | Baisse de stats et de qualité de récompenses de quête de donjon pendant la bêta | INDEXÉ (DE) |
| Warcraft Tavern — familier | https://www.warcrafttavern.com/forever/guides/hunter-pets/ · https://www.warcrafttavern.com/forever/guides/hunter-pet-abilities/ | Loyauté, points de dressage, 10 % de PA et 100 % de critique hérités | INDEXÉ (guides de bêta) |
| Formateurs paladin mort-vivant | https://warcraft.wiki.gg/wiki/Aramis_Hammerhand · https://warcraft.wiki.gg/wiki/Garen_Largo · https://www.warcrafttavern.com/forever/guides/class-trainers/ | Aramis Hammerhand (Deathknell), Shari Stilwell (Brill), capitale à Fossoyeuse | INDEXÉ (guides divergent sur le formateur de capitale) |
| Entrées des donjons Forever | https://www.warcrafttavern.com/forever/guides/the-drowned-city/ · https://www.warcrafttavern.com/forever/guides/alcaz-island-prison/ · https://www.icy-veins.com/wow/news/kroldok-stronghold-dungeon-level-range-change-all-9-dungeons-listed/ | Cité submergée sous l'eau (`/way 21.4 27.9`), île d'Alcaz, Krol'dok 40-45 | INDEXÉ (en partie issu de la bêta) |
| GDKP interdits | https://www.icy-veins.com/wow-forever/news/blizzard-just-confirmed-gdkp-runs-wont-be-allowed-in-wow-forever/ · https://www.gamesradar.com/games/world-of-warcraft/wow-forever-doesnt-allow-gdkp-blizzard-says-the-new-mmos-economy-is-something-were-taking-very-seriously/ · https://www.invenglobal.com/articles/27234/world-of-warcraft-forever-to-allow-gdkp-in-korea | Interdiction annoncée au Q&R du 17/09/2026 ; NA et EU seulement selon Inven | INDEXÉ (relais de presse, 18/11/2026) |
| Achat d'or et sanctions | https://www.icy-veins.com/wow-forever/news/blizzard-reiterated-gold-buying-rules-for-wow-forever/ · https://www.gamesradar.com/games/world-of-warcraft/world-of-warcraft-forever-aims-to-aggressively-shut-down-the-flow-of-suspicious-gold-but-blizzard-warns-there-may-be-false-positives-at-first/ · https://www.warcrafttavern.com/forever/news/blizzard-intensifies-their-battle-against-gold-buying-in-wow-forever/ | Suppression d'or, suspension, bannissement ; faux positifs possibles | INDEXÉ (403 à la lecture) |
| Champs de bataille | https://conquestcapped.com/guides/wow-forever/wow-forever-warsong-gulch-battleground/ · https://www.skill-capped.com/wowarticles/forever/tier-lists/forever-battlegrounds/ | Tranches de niveaux (Goulet 10+, Arathi 20+, Alterac 51-60, Sombrelances 30-60) | INDEXÉ (guides, disponibilité au lancement divergente) |
| Forum EU — file de champ de bataille | https://eu.forums.blizzard.com/en/wow/t/wow-forever-unable-to-join-battlegrounds/642988 | File solo qui ne se lance pas, file de groupe OK (15-17/11/2026) | VÉRIFIÉ (page lue, sans réponse Blizzard) |
| Lore du paladin réprouvé | https://www.pcgames.de/World-of-Warcraft-Spiel-42971/Specials/Die-tragische-Geschichte-der-untoten-Paladine-1556975/ · https://kami-labs.fr/en/wow-forever/inebranlable-wow-forever-paladin-reprouve/ | Garek Bandarion, nouvelle « Unbowed » du 26/10/2026 | INDEXÉ |

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
| Kami-Labs — quêtes buguées | https://kami-labs.fr/wow-forever/bugs-quetes-wow-forever/ | Tableau des quêtes buguées et corrigées, avec statut daté | VÉRIFIÉ (état au 07/11/2026, à revérifier) |
| Kami-Labs — niveau 40 | https://kami-labs.fr/en/wow-forever/wow-forever-niveau-40-monture-double-specialisation/ | Monture (100 po, 1re monture incluse) et double spé au 40 ; chiffres de bêta | VÉRIFIÉ (31/10/2026, bêta) |
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
| Code de l'interface Forever | https://github.com/Gethe/wow-ui-source (branche `forever`) | Extraction du FrameXML et de la documentation d'API (`Blizzard_APIDocumentationGenerated`) du client Forever : signatures exactes des fonctions `C_*`, événements, tooltips et cadres. Référence pour l'addon (lecture du code, pas d'appel en jeu) ; ne dit rien du gameplay | INDEXÉ (branche à recouper avec le build du client) |
| Doc générale | https://warcraft.wiki.gg/wiki/TOC_format · https://warcraft.wiki.gg/wiki/Getting_the_current_interface_number | — | INDEXÉ |
| Addons Forever | CurseForge (p. ex. ClassicUI Forever, QuietUI, XE QoL Forever), Wago | — | INDEXÉ |

## Top 5 fiabilité

1. Blizzard News (FR/EN) : officiel et terminologie FR.
2. warcraft.wiki.gg (`/wiki/Forever` + pages `_(Forever)`) : le plus complet et à jour.
3. Forums Blizzard US, catégorie 346 : posts bleus, bugs connus.
4. Wowhead `/forever` (et `/forever/fr`) : base de données et actualités.
5. Warcraft Tavern `/forever/` et Icy Veins `/wow-forever/` : guides de classe et de leveling (à lire hors outil automatique, 403).
