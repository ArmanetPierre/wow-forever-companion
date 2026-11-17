# Comparaison : wow-forever-companion et chelinho139/wow-ai

Statut : **analyse, rien n'est développé.** Date : 17/11/2026.
Source : https://github.com/chelinho139/wow-ai, lu en lecture seule (clone local, aucun code exécuté),
41 commits du 23/09/2026 au 04/11/2026, licence MIT, page CurseForge « ai-agents-chat ».

## 1. Ce qu'est wow-ai

**Un chat dans le jeu qui pilote des agents de code en local.** Le joueur tape un message dans une
fenêtre de l'addon. Un pont Node.js le récupère et lance Claude Code, Codex, Grok, Antigravity ou
Hermes en mode sans interface, dans un dossier de projet. La réponse revient dans le jeu.
Le cas d'usage principal est de **coder sans quitter le jeu** (« send a task, go back to questing »).
L'aide au jeu est un usage secondaire : un contexte de partie, des macros et des marques sur la carte.

| Point | Ce qu'il fait |
|---|---|
| Version du jeu | WoW: Forever (TOC 16001, client `_forever_`), auparavant la bêta |
| Architecture | Addon Lua d'un seul fichier (`WoWAI.lua`, 3 153 lignes), plus `Map.lua` et `Codec.lua`. Pont Node sans dépendance (`bridge.js`, `protocol.js`, `agents.js`), avec un superviseur qui le relance. |
| Jeu → pont | **Lecture de l'écran.** L'addon dessine le message en carrés de 4×4 px (3 bits par case, 8 couleurs pures) dans le coin haut-gauche. Le pont capture ce coin 4 fois par seconde : `capture.ps1` (GDI), `capture_x11.py` (X11 sous Wine) ou `capture_mac.py` (`screencapture`, avec les permissions Enregistrement d'écran et Automation). Les messages sont limités à environ 3,2 Ko. |
| Pont → jeu | 200 addons « emplacements » chargés à la demande (`WoWAI_S001…S200`). Le pont réécrit les 200 `Inbox.lua` et le jeu en charge un nouveau selon un calendrier. Des signaux passent par des `.wav` vides ou valides : `PlaySoundFile` renvoie vrai ou faux. L'installation crée environ 15 000 petits fichiers. |
| LLM | Les CLI installées chez le joueur, une par chat. Les sessions reprennent (`--resume`) et s'exécutent en parallèle (`maxParallel`). |
| Contexte de jeu | `GameContext()` donne la version, le perso, la guilde, la zone, les coordonnées, l'argent, l'XP, les talents, les métiers et les identifiants de quêtes, en 900 octets au plus. S'y ajoutent les infobulles des objets liés par Maj-clic. |
| Fonctions en plus | Macros prêtes à l'emploi avec un bouton « Create macro » (et un avertissement « runs code » pour `/run` et `/click`). Calques sur la carte du monde et navigateur à flèche. Points de récolte (addon de données optionnel). Écho `TL;DR:` dans le chat du jeu. `/r` vers l'agent. Bouton « Allow & retry » pour les permissions. |
| Installation | `node setup.js`, Node 22.2 ou plus, une CLI d'agent. Fenêtré ou plein écran fenêtré obligatoire. Guides pour Windows, Linux (Wine) et macOS. |
| Tests | 11 fichiers (environ 2 500 lignes) : addon exécuté dans une VM Lua avec un faux client (`wow_stub.lua`), codec, protocole, agents (fixtures JSONL de chaque CLI), carte, macros, restauration. CI GitHub Actions sur Windows et Ubuntu. |

## 2. Comparaison point par point

| Axe | Nous (wow-forever-companion) | wow-ai |
|---|---|---|
| **Finalité** | Compagnon de jeu qui conseille, avec des réponses sourcées | Terminal de code dans le jeu, avec une aide de jeu secondaire |
| **Capture** | ~15 domaines riches (équipement avec stats, sacs, banque, quêtes avec récompenses, métiers, talents, familier, réputations, sorts…), stockés dans des SavedVariables | Un contexte texte de 900 octets, reconstruit à chaque message |
| **Transport et fraîcheur** | SavedVariables écrites au /reload ou à la déconnexion, touche Sync (Ctrl+Maj+S), en-tête de fraîcheur | Quasi temps réel (capture 4 fois par seconde), mais **seulement par lecture de l'écran** |
| **Sens jeu → IA → jeu** | Sens unique (le jeu vers l'IA) : on répond hors du jeu | Aller-retour complet : on pose la question et on lit la réponse dans le jeu |
| **Connaissance du jeu** | Base SQLite locale construite depuis le client (CASC, DB2 et hotfixes Forever), `knowledge/`, mémoire de recherche ; QuestieDB prévu | **Aucune** : « The bridge ships no game data ». Le modèle répond de mémoire, ou le joueur fournit ses propres données. |
| **Outils exposés à l'IA** | 26 outils MCP typés (`get_overview`, `find_upgrades`, `compare_item`, `get_quest_rewards`…) | Aucun outil de jeu. Un fichier `WOW_AI_MAP_FILE` en JSONL et des blocs ```` ```wowmap ```` / ```` ```wowmacro ```` dans la réponse. |
| **Format de réponse** | Charte : en-tête, verdict en gras, badges `[Forever]`, `[Classic]`, `[Retail]` | Libre, avec un `TL;DR:` final imposé pour l'écho dans le chat |
| **Multi-perso et multi-utilisateur** | Index des persos, `set_active_character`, `compare_characters`, comptes rattachés à un prénom | Un seul contexte, celui du perso connecté (plusieurs chats, mais pas plusieurs persos) |
| **i18n** | frFR complet, enUS en cours | Anglais seulement (interface et prompts) |
| **Plateformes** | Python stdlib 3.9+ ; Mac testé, Windows et Linux non testés | Windows, Linux sous Wine (X11 seulement, pas Wayland) et macOS testés par des contributeurs ; plein écran exclusif non pris en charge |
| **Vie privée** | Tout reste en local, données perso hors du repo (`~/WowForever/`) | Local aussi, mais le contexte part à 5 fournisseurs d'IA possibles (guilde comprise). Une capture d'écran est demandée en permanence. |
| **Partage** | Marketplace de plugin Claude Code, licence MIT | CurseForge et `npm link`, licence MIT |
| **Tests** | Addon (189 vérifications), MCP (35 tests), gamedata, e2e, banc d'essai `docs/evals/` ; **pas de CI** | Tests unitaires et d'intégration, faux client Lua, **CI sur 2 OS** |
| **Docs** | Plans de conception, schémas, inventaire des API | ARCHITECTURE, CONFIGURATION, AGENTS et guides d'installation par OS, très détaillés et à jour |
| **CGU Blizzard** | Rien d'autre que l'API d'addon et la lecture de fichiers du client (lecture seule) | Lecture de l'écran : **c'est la technique des « pixel bots »**. Rien n'injecte de code ni ne simule de touche, mais c'est une zone grise (voir 4.1). |

## 3. Bonnes idées à reprendre

| # | Idée | Bénéfice pour nous | Module visé | Effort | Licence |
|---|---|---|---|---|---|
| B1 | **Fausse API WoW pour tester l'addon** (`tests/wow_stub.lua` et une VM Lua qui joue une session entière : connexion, événements, réponse) | Tester `ForeverScribe` sans le jeu, au-delà des vérifications statiques ; valider les sorties enUS et frFR | `addon/` et tests | Moyen | MIT, compatible (on peut s'en inspirer, voire copier avec mention) |
| B2 | **CI GitHub Actions multi-OS** (Windows et Ubuntu) | Combler notre trou « Windows et Linux non testés » pour le MCP Python et `gamedata/` | `.github/workflows/` | Faible | Simple pratique, rien à copier |
| B3 | **Liens Maj-clic développés en infobulle** (`ExpandLinks` : `|Hitem:…|h` lu via un `GameTooltip` caché) | Capturer l'infobulle texte des objets (stats aléatoires « de l'Aigle », effets) que la base ne calcule pas : c'est une de nos limites | Collecteurs `ForeverScribe` (sacs, récompenses) | Faible | Technique d'API publique |
| B4 | **Bloc « primer » relu à chaque exécution** (`WOW-ADDON-PRIMER.md` : `C_*` modernes, cales de compatibilité 12.x, « vérifier dans Gethe/wow-ui-source, branche forever ») | Un fichier court de règles Forever injecté dans l'agent, distinct des skills ; il réduit les erreurs « mémoire Classic ». La référence **wow-ui-source branche `forever`** est à ajouter à `knowledge/sources.md`. | `knowledge/` et agent | Faible | Idée seulement |
| B5 | **Résumé court exigé de l'agent** (`TL;DR:`) et coupé par le code | Matérialiser notre « verdict en premier » sous une forme qu'on peut vérifier dans `docs/evals/` (le verdict doit tenir sur une ligne) | Charte de réponse, banc d'essai | Faible | Idée |
| B6 | **Macros générées avec garde-fou** (bloc structuré, bouton qui crée la macro, avertissement si `/run`, `/click` ou `/script`, commande d'annulation) | Un vrai « rends-moi service » pour le chasseur (macro familier, Tir automatique). Pour nous, un bloc à copier suffit d'abord, sans écriture en jeu. | Skills `talents` et `familier` | Faible (texte) à moyen (en jeu) | Idée |
| B7 | **Itinéraire sur la carte** (calques de points `uiMapID` et x,y, navigateur) | Le prolongement naturel de QuestieDB : « tes 5 objectifs dans l'ordre » sous forme de chaîne `/way`, puis plus tard des repères en jeu | MCP (`plan_route` produisant des `/way`), plus tard l'addon | Moyen | Idée ; leurs données de récolte ne sont pas fournies |
| B8 | **Robustesse face aux effacements de SavedVariables** (le pont garde une copie et restaure) | Notre MCP garde déjà les snapshots : on peut l'écrire noir sur blanc et détecter un `ForeverScribeCharDB` vidé | `sync.py` | Faible | Idée |
| B9 | **Docs d'installation par OS avec dépannage et commande « probe »** | Une commande `doctor` qui vérifie le chemin du jeu, la présence de l'addon, les SavedVariables trouvées, la base construite et la locale | MCP ou `tools/` | Faible | Idée |
| B10 | **Même position que nous sur les données sous licence** : « QuestieDB… their licences don't allow redistributing them here, so that folder stays yours » | Cela confirme notre choix de télécharger QuestieDB chez chaque joueur, sans le copier dans le repo | QuestieDB | — | Confirmation |

## 4. Mauvaises idées et risques

1. **Transport par lecture de l'écran.** Ils le présentent honnêtement (pas d'injection de code, pas de
   simulation de touche), mais c'est techniquement la même chaîne que les « pixel bots » de rotation,
   que Blizzard sanctionne. Le risque dépend de l'usage plus que de la technique, mais c'est un signal
   qui se détecte et qu'il faut éviter : **on ne le reprend pas.**
   Inconvénients pratiques : le plein écran exclusif est cassé, Wayland est impossible, macOS demande
   l'enregistrement d'écran permanent, 3,2 Ko au plus, et la bande de couleur reste visible à l'écran.
2. **Installation lourde et bricolée** : 200 faux addons et environ 15 000 fichiers, astuce des `.wav`
   vides ou valides (avec auto-test parce que « some clients report an empty file as playable »),
   fichiers découverts seulement au lancement du jeu. Tout cela est fragile au moindre changement
   du client et pollue la liste des addons.
3. **Un agent de code avec des droits d'écriture, piloté depuis un chat dans le jeu.**
   - Mode par défaut `acceptEdits` ; `bypassPermissions` et le Codex sans bac à sable sont proposés.
   - Le bouton « Allow & retry » ajoute des règles d'autorisation permanentes dans `config.json` depuis le jeu.
   - Les infobulles et le contexte de jeu entrent dans le prompt : c'est une **surface d'injection de prompt**.
     Par exemple, un objet au nom piégé, ou un autre addon qui dessinerait une fausse bande, car tout ce qui
     est à l'écran est lu.
   - Pour nous, l'agent est en lecture seule sur les données du jeu : c'est à garder.
4. **Aucune connaissance du jeu.** Le modèle répond de mémoire. C'est exactement le défaut que notre
   retour du 17/11 a mesuré (casque conseillé à tort, 107 k tokens de recherche web). wow-ai repousse
   le problème vers l'utilisateur (« point the chat at a folder that holds game data »).
5. **Contexte pauvre et recalculé**, avec des coupes silencieuses à 900 octets : pas d'équipement chiffré,
   de sacs, de récompenses ni d'historique. On ne peut pas comparer d'objets ni suivre une progression.
6. **Un fichier Lua de 3 153 lignes** (« a single file »), plus dur à relire et à contribuer que nos
   collecteurs par domaine.
7. **Taint** : il remplace les fonctions de la zone de saisie du chat (`ProcessChatType`, `SendMessage`,
   `SendText`) pour `/r`. L'issue #29 montre la contamination qui en résulte. À ne pas imiter : chez nous,
   seulement `hooksecurefunc`, et rien sur le chat.
8. **Fuite de données vers plusieurs fournisseurs** : nom, royaume, guilde et position partent à
   l'IA par défaut (désactivable avec `/wow-ai context off`). Tout est opt-out, rien n'est opt-in.

## 5. Bilan

**Nous faisons mieux :**
- de vraies données de jeu Forever en local (objets et correctifs) et des outils typés ;
- une capture riche et structurée, avec des réponses sourcées et des badges de certitude ;
- le multi-perso et le multi-utilisateur ;
- le français ;
- le respect des CGU sans zone grise, et un agent qui n'a aucun droit d'écriture sur le système.

**Ils font mieux :**
- l'aller-retour dans le jeu sans /reload ;
- la fraîcheur en temps réel ;
- l'intégration aux CLI d'agents (5 fournisseurs) ;
- des tests de l'addon avec un faux client, et une CI sur 2 OS ;
- des docs d'installation par OS testées par des contributeurs ;
- des sorties actionnables dans le jeu (macros, carte, navigateur) ;
- une publication sur CurseForge.

**Ce qui est complémentaire :** leur modèle « IA dans le jeu » et notre modèle « IA qui connaît le jeu ».
Une passerelle propre sans lecture de l'écran n'existe pas aujourd'hui : notre position
« question hors du jeu, réponse riche » reste la bonne.

## 6. Recommandations (top 5, classées)

| Rang | Recommandation | Chantier lié | Pourquoi maintenant |
|---|---|---|---|
| 1 | **Faux client WoW et tests d'addon en VM Lua** (B1), avec un cas enUS et un cas frFR | **Anglais** | Le chantier anglais touche toutes les chaînes de l'addon : seul un faux client permet de vérifier `Locales.lua` et les collecteurs sans lancer deux clients |
| 2 | **CI GitHub Actions** sur macOS, Windows et Ubuntu, pour les tests MCP, gamedata et addon (B2) | Anglais (et la publication) | Elle supprime la mention « Windows et Linux non testés » pour la partie Python ; c'est un faible coût |
| 3 | **Fichier « primer » Forever court, injecté dans l'agent** (B4), et le verdict d’une ligne vérifié dans le banc d'essai (B5) | **Optimisation de l'agent** | Moins de réponses « mémoire Classic » et une mesure de la qualité du format dans `docs/evals/` ; ajouter `Gethe/wow-ui-source` (branche `forever`) aux sources |
| 4 | **Itinéraire de quêtes en `/way`** (B7) : à partir des coordonnées QuestieDB, un outil qui ordonne les objectifs et rendus du journal et sort une liste de `/way` ; les repères dans l'addon viendront plus tard | **QuestieDB** | C'est la valeur la plus visible de l'intégration des quêtes ; leur doc confirme qu'on ne redistribue pas les données |
| 5 | **Infobulle texte des objets via un `GameTooltip` caché** (B3), dans les collecteurs de sacs et de récompenses | Optimisation de l'agent (et la limite « stats aléatoires ») | Elle couvre les objets à suffixe aléatoire et les effets que la base ne calcule pas, sans transport nouveau |

**À ne pas reprendre :**
- le transport par lecture de l'écran ;
- les emplacements chargés à la demande et l'astuce des `.wav` ;
- le remplacement des fonctions du chat ;
- les droits d'écriture donnés à l'agent depuis le jeu.

À reconsidérer seulement si Blizzard ouvre un jour une voie officielle (aucune aujourd'hui).
