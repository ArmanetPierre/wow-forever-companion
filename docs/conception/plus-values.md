# Plus-values encore inexploitées du compagnon WoW Forever

Étude du 18/11/2026, en lecture seule. Sources lues : README, `docs/schema.md` (v1.4),
`docs/api-inventaire.md` et `docs/sonde/fonctions.txt`, agent `forever-guide`, les 8 skills,
`knowledge/`, `docs/conception/`, `docs/comparaison/bilan.md`, la base locale
`la base locale` et les outils appelés en lecture sur Brannok et Elwyn.

## Ce qui ressort de l'existant

- **Notre force prouvée** (bilan) : tout ce qui touche au perso réel et à la base du client
  (C01-C04 : 12/12 contre 3 à 8). Sur l'actualité, ChatGPT est à égalité ou presque.
  **Conclusion : chaque nouvelle idée doit s'appuyer sur des données que seul l'addon ou la base
  locale possède.** Ce qui relève du « savoir général » n'apporte rien de plus.
- **Le compagnon est surtout un instantané.** L'addon capture l'état présent. Le serveur garde
  **un instantané par jour** (`historique/AAAA-MM-JJ.json`) et `overview vue=progres` fait un
  diff grossier. Rien ne mesure le **rythme** (XP/h, or/h, temps en ville), les **sessions**, les
  **morts**, ni les **prix**.
- **Le compagnon voit un perso à la fois.** `characters comparer` existe, mais aucun outil ne
  raisonne sur **le compte entier** (sacs + banque + courrier de tous les persos).
- **Le compagnon répond à une question ; il ne planifie pas.** Rien ne relie une échéance
  (raids le **09/12/2026**, monture au niveau 40 à **100 po**, Hardcore cet hiver) à l'état et au
  rythme réels du joueur.
- **API disponibles et pas encore exploitées** (présentes dans `fonctions.txt`) :
  `C_AuctionHouse.*` (86 fonctions, API moderne), `C_TaxiMap.GetAllTaxiNodes`,
  `GetInboxNumItems`/`GetInboxItem`/`GetInboxItemLink`, `C_DamageMeter.*` (8 fonctions),
  `C_ChatInfo.SendAddonMessage`, `C_GuildInfo.QueryGuildMembersForRecipe`,
  `C_DateAndTime.GetSecondsUntilWeeklyReset`, `C_PerksActivities.*`, `C_DeathInfo.*`.
- **API absentes** (à ne pas promettre) : journal de combat (`CombatLogGetCurrentEventInfo`
  absent), verrous d'instance (`GetSavedInstanceInfo`, `GetNumSavedInstances` absents),
  `GetInboxHeaderInfo` absent (expéditeur et argent des lettres à sonder autrement).
- **Base locale riche et sous-utilisée** : `q_quests.rep_reward` (réputation par quête),
  `items.sell_price`/`buy_price`, `recipes` (jaune/vert/gris, composants), `q_npcs.npc_flags`
  (marchands, formateurs, maîtres de vol), `q_spawns` (80 313 positions).

Rappel des règles qui bornent tout : aucune action automatisée, rien en combat, chaque
collecteur dans `pcall`, `ReloadUI` seulement sur geste du joueur. **Le flux est à sens unique**
(l'addon ne peut pas lire ce que l'agent écrit) : toute aide « en jeu » passe par un texte que
le joueur colle lui-même (`/way`, macro) ou lit avant de jouer.

---

## Les idées, classées par valeur / effort

| # | Idée | Valeur | Effort | Données |
|---|---|---|---|---|
| 1 | Circuit de session optimisé | très forte | M | presque tout là ; + vols connus |
| 2 | Journal de session et rythme réel | forte (fondation) | M | à ajouter dans l'addon |
| 3 | Plan de campagne vers une échéance (raids 9/12, monture 40) | très forte | M | là + idée 2 |
| 4 | Inventaire de compte (tous persos, banque, courrier) | forte | S-M | presque tout là ; + courrier |
| 5 | Prix de l'hôtel des ventes capturés | forte (joueurs avancés) | M | à ajouter dans l'addon |
| 6 | Check-list « avant de partir » et alertes de régression | moyenne-forte | S | là à 90 % |
| 7 | Plan de réputation | moyenne (forte au 60) | S-M | là (base + capture) |
| 8 | Copilote Hardcore | forte pour un public précis | M | là + mort à capturer |
| 9 | Bilan de combat (compteur de dégâts intégré) | moyenne-forte | M-L | à sonder puis ajouter |
| 10 | Groupe et guilde | moyenne | L | à ajouter (messages d'addon) |
| 11 | Héritage (Legacy) à l'échelle du compte | moyenne | L | API inconnue, à sonder |

---

### 1. Circuit de session optimisé — valeur très forte, effort M

- **Problème du joueur** : Brannok a 13 quêtes à rendre, 40 en cours, des objectifs éparpillés
  entre les Paluns, la marche de l'Ouest et Auberdine. Il perd 20 minutes en allers-retours et
  oublie une quête à rendre juste à côté du maître de vol.
- **Ce que fait l'agent** : « J'ai 1 h 30 ce soir. » → un circuit ordonné : rendre ici, prendre
  là, objectifs groupés par zone, vol à prendre, moment où utiliser la pierre de foyer, et un
  bloc de `/way` à coller (TomTom ou carte), avec la carte `map` de chaque étape. Il estime l'XP
  gagnée et le niveau atteint en fin de soirée (table d'XP de la base).
- **Données** :
  - capturées : quêtes, objectifs et coordonnées (`GetQuestsOnMap`), quêtes terminées,
    position, lieu de la pierre de foyer (`GetBindLocation`), XP ;
  - base locale : donneurs et finisseurs (`q_npcs`, `q_spawns`), maîtres de vol
    (`npc_flags`), zones, XP des quêtes ;
  - **à ajouter** : les vols **connus** du perso, via `C_TaxiMap.GetAllTaxiNodes(mapID)` à
    l'événement `TAXIMAP_OPENED` (fenêtre de vol ouverte par le joueur ; état « connu / non
    connu » par nœud). Option : temps de recharge de la pierre de foyer
    (`C_Container.GetContainerItemCooldown`, présent).
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : ils ne voient ni le journal, ni les
  coordonnées, ni les vols connus. Le bilan montre qu'ils inventent les quêtes et les
  coordonnées (C01, C03).
- **Effort** : M. Un algorithme glouton par zone (plus proche voisin + regroupement par zone et
  vol) suffit ; pas besoin d'un vrai solveur.
- **Risques** : distances « à vol d'oiseau » (relief, murs) → le dire ; quêtes de groupe ou
  élites à signaler. Aucun risque Blizzard : rien n'est automatisé, le joueur colle les `/way`.

### 2. Journal de session et rythme réel — valeur forte (fondation), effort M

- **Problème du joueur** : « J'ai joué 3 h hier soir, j'ai l'impression de n'avoir rien fait. »
  Le compagnon ne peut aujourd'hui répondre que « Aucun changement notable » (diff journalier).
- **Ce que fait l'agent** : un **résumé de soirée** automatique dans `journal.md` (quêtes rendues,
  niveaux, or gagné et dépensé, objets obtenus, morts, temps en ville / en vol / en combat), et
  des **chiffres de rythme** : XP par heure par zone, or par heure, temps moyen par niveau. Il
  repère ce qui coûte du temps : « 40 % de ta soirée en ville », « la zone X te rapporte 2 fois
  moins d'XP/h que Y ».
- **Données** :
  - capturées : `timePlayed` (total et au niveau), XP, argent, position (instantanés) ;
  - **à ajouter** : un domaine `sessions` en **tampon circulaire** (taille bornée) :
    début et fin de session (`PLAYER_LOGIN`, `PLAYER_LOGOUT`, `time()`), changements de zone
    horodatés (`ZONE_CHANGED_NEW_AREA`), quêtes rendues avec XP et argent
    (`QUEST_TURNED_IN` fournit les deux), montées de niveau avec `timePlayed`, morts
    (`PLAYER_DEAD` : horodatage, zone, niveau, nom de la cible), butin notable
    (`CHAT_MSG_LOOT`, qualité ≥ vert). Passer par `docs/schema.md` (version mineure 1.5).
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : aucune mémoire fiable du jeu réel ; le joueur
  ne saisira jamais ces chiffres à la main.
- **Effort** : M (addon : collecteur léger sur événements, pas de travail en combat ;
  serveur : agrégation + section auto du journal).
- **Risques** : taille du fichier SavedVariables → tampon borné (par ex. 30 sessions, 500
  événements). Les événements arrivent aussi en combat : seulement **ajouter une ligne** à une
  table (pas d'appel coûteux) ; toute analyse se fait côté serveur. `pcall` partout.

### 3. Plan de campagne vers une échéance — valeur très forte, effort M

- **Problème du joueur** : « Je veux être prêt pour les raids du 9 décembre » ou « je veux ma
  monture au 40 ». Brannok est niveau 25 avec 2 po 40 ; la monture coûte 100 po (prix de bêta,
  à vérifier) et les raids exigent le niveau 60 et, pour Onyxia, l'Amulette drakefeu.
- **Ce que fait l'agent** : un plan **semaine par semaine** chiffré à partir du **rythme réel**
  (idée 2) : date probable du 40 et du 60 ; or nécessaire et écart à combler (« il te manque
  97 po : vends ces 22 Cuir moyen, monte le dépeçage, garde ces composants ») ; étapes de
  l'harmonisation d'Onyxia déjà faites ou non (via `questsCompleted`) ; donjons de la chaîne ;
  consommables et résistances à prévoir. Il est **franc** : « à ton rythme (6 h/semaine), le 60
  arrive vers fin janvier : vise d'abord… ». Le plan va dans `objectifs.md` et l'agent le
  compare au réel à chaque synchro (« en avance de 2 jours »).
- **Données** :
  - capturées : niveau, XP, `timePlayed`, argent, quêtes terminées, métiers, résistances
    (`UnitResistance` dans `stats`), réputations ;
  - base locale : table d'XP du client, chaîne des quêtes (`pre_single`, `next_in_chain`),
    prix des objets, donjons ;
  - connaissances : échéances et prix datés dans `forever-essentiels.md` ;
  - **à ajouter** : le rythme (idée 2). Sans lui, le plan repose sur des heures déclarées.
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : ils connaissent l'annonce des raids mais ni le
  rythme du joueur, ni ses quêtes faites, ni son or ; leurs plans restent génériques.
- **Effort** : M (une skill `forever-objectifs` ou extension de `forever-leveling` + un outil de
  projection côté serveur).
- **Risques** : prix et étapes encore « à vérifier » dans la base de connaissances → badges et
  certitude obligatoires. Aucun risque Blizzard.

### 4. Inventaire de compte (tous persos, banque, courrier) — valeur forte, effort S-M

- **Problème du joueur** : « Où j'ai mis mes Étoffes de laine ? », « Mon reroll prêtre récolte
  des herbes, mon chasseur a besoin de quoi ? », banque pleine de choses inutiles.
- **Ce que fait l'agent** : recherche d'un objet sur **tous les persos** (sacs, banque,
  courrier) ; propose des **transferts entre persos** (« envoie 10 Étoffe de laine de Brannok à
  Elwyn pour le secourisme ») ; repère les composants d'une recette répartis entre persos ; trie
  la banque (gris, objets de quêtes terminées, composants de métiers abandonnés) ; signale les
  lettres qui vont expirer.
- **Données** :
  - capturées : sacs de chaque perso, banque (à l'ouverture), métiers de chaque perso ;
  - base locale : recettes et composants, quêtes terminées → objets devenus inutiles ;
  - **à ajouter** : le **courrier** à l'ouverture de la boîte (`MAIL_SHOW`,
    `MAIL_INBOX_UPDATE`, `GetInboxNumItems`, `GetInboxItem`, `GetInboxItemLink` présents ;
    `GetInboxHeaderInfo` **absent** → expéditeur, argent et date d'expiration à sonder via
    `C_Mail` ou `C_TooltipInfo.GetInboxItem`).
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : ils ne voient aucun sac, encore moins ceux de
  plusieurs persos.
- **Effort** : S pour sacs + banque (déjà capturés, il manque un outil « compte »), M avec le
  courrier.
- **Risques** : la banque n'est vraie qu'à la dernière ouverture → afficher la fraîcheur par
  perso et par lieu. Rien d'automatique : le joueur envoie lui-même le courrier.

### 5. Prix de l'hôtel des ventes capturés — valeur forte pour les joueurs avancés, effort M

- **Problème du joueur** : « Je vends ces 22 Cuir moyen au marchand ou à l'HV ? », « Quel
  métier rapporte en ce moment ? », « Ma pièce verte vaut combien ? ». Il n'existe pas de site de
  prix fiable pour les méga-royaumes Forever, et l'addon de prix habituel n'est peut-être pas
  porté.
- **Ce que fait l'agent** : valeur réelle des sacs et de la banque (HV contre marchand, avec
  `sell_price` de la base comme plancher) ; « garde / vends / mets en vente à X » ; rentabilité
  d'une recette (prix du produit moins prix des composants) et chemin de montée de métier le
  moins cher ; suivi de **mes ventes** (expirées, invendues, prix trop haut). Avec l'historique
  des captures : tendance sur plusieurs jours.
- **Données** :
  - base locale : `items.sell_price`, `buy_price`, recettes et composants ;
  - **à ajouter** : capture **passive** des recherches **que le joueur fait lui-même** :
    `AUCTION_HOUSE_BROWSE_RESULTS_UPDATED`, `COMMODITY_SEARCH_RESULTS_UPDATED`,
    `ITEM_SEARCH_RESULTS_UPDATED` → `C_AuctionHouse.GetBrowseResults`,
    `GetCommoditySearchResultInfo`, `GetItemSearchResultInfo` (prix minimum, quantité, horodatage
    par objet) ; mes ventes via `OWNED_AUCTIONS_UPDATED` → `GetOwnedAuctions`. En option, un
    **bouton « relever les prix »** (geste du joueur) qui appelle `C_AuctionHouse.ReplicateItems`
    une fois (API limitée par Blizzard à un appel toutes les ~15 min en retail, **à vérifier**
    dans Forever). Les noms d'événements viennent du retail : **à sonder en jeu**.
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : aucun prix Forever par méga-royaume et par
  faction ; ils citent des prix Classic de 2019.
- **Effort** : M (collecteur à l'ouverture de l'HV, stockage compact par itemID ; outil `prix`).
- **Risques** : **pas de recherche automatique** (une recherche lancée par code sans geste du
  joueur serait une automatisation) → seulement lire ce que le joueur affiche, ou un bouton.
  Données partielles et vite périmées → toujours dater et dire « prix vu le … sur N objets ».
  Rien sur les GDKP (interdits). Taille du fichier : garder le minimum par objet.

### 6. Check-list « avant de partir » et alertes de régression — valeur moyenne-forte, effort S

- **Problème du joueur** : il part en donjon avec 40 % de durabilité, 200 balles, un familier
  mécontent et 2 points de talent non dépensés ; ou il équipe une arme d'un autre type et sa
  compétence d'arme est à 1.
- **Ce que fait l'agent** : à chaque synchro, une liste courte « à régler avant de partir » :
  durabilité et coût de réparation, munitions selon la durée prévue (consommation estimée par le
  rythme), nourriture du familier, sacs pleins, points de talent, **sorts à acheter chez le
  maître de classe et leur coût total** (sorts de la base au niveau ≤ actuel, absents du livre
  de sorts), compétence d'arme basse, XP de repos au plafond, objets à **ne pas vendre** (la
  restauration d'objets est désactivée depuis le 11/11). Les **régressions** : armure,
  PA ou DPS en baisse depuis la veille, loyauté du familier qui chute.
- **Données** : tout est capturé ou en base (équipement et durabilité, stats, sorts, talents,
  familier, sacs, `C_SkillInfo`, `spells.spell_level`). Le serveur a déjà une partie de ces
  rappels dans `overview` (munitions < 200, rangs chez le formateur).
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : il faudrait que le joueur leur décrive tout son
  état à chaque fois.
- **Effort** : S (règles côté serveur, une section du verdict de `overview`).
- **Risques** : trop d'alertes = bruit → au plus 3 lignes, par ordre d'importance.

### 7. Plan de réputation — valeur moyenne (forte au niveau 60), effort S-M

- **Problème du joueur** : « Combien de quêtes pour être Honoré à Forgefer ? », plus tard
  Aube d'argent, Grumegueules ou factions propres à Forever.
- **Ce que fait l'agent** : points restants jusqu'au palier visé ; quêtes **du journal** et
  **disponibles** qui donnent de cette réputation (et combien) ; récompenses débloquées au palier.
- **Données** : capturées (`reputations`, paliers et seuils) ; base locale
  (`q_quests.rep_reward`, quêtes disponibles, quêtes terminées). Rien à ajouter dans l'addon.
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : ils ne savent pas où en est le joueur ni quelles
  quêtes il a déjà faites.
- **Effort** : S-M (outil `reputations` enrichi).
- **Risques** : factions et récompenses propres à Forever mal connues → badges.

### 8. Copilote Hardcore — valeur forte pour ce public, effort M

- **Problème du joueur** : en Hardcore (ouverture cet hiver), une quête mal jugée tue le perso :
  élite caché, mobs 3 niveaux au-dessus, patrouille, objectif dans une grotte.
- **Ce que fait l'agent** : un **indice de risque** par quête du journal et par étape du
  circuit (niveau et rang des mobs de la base, élites, quêtes de groupe, densité de spawns),
  un plan de fuite (Feindre la mort, potions en sacs, chemin), et après une mort sur un autre
  ruleset ou un « presque » : un **post-mortem** (zone, niveau, cible, vie et ressources).
- **Données** : capturées (quêtes, niveau, sacs, sorts) ; base locale (`q_npcs.min_level`,
  `rank`, `q_spawns`) ; `C_GameRules.IsHardcoreActive` ; **à ajouter** : la mort (idée 2).
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : pas de niveaux de mobs fiables pour Forever ni
  de vue du journal ; Gemini plaque déjà des règles Classic.
- **Effort** : M.
- **Risques** : un conseil de sécurité faux coûte un perso → certitude affichée, prudence par
  défaut. Rien en combat (pas de « coach » en temps réel, impossible et interdit).

### 9. Bilan de combat via le compteur de dégâts intégré — valeur moyenne-forte, effort M-L

- **Problème du joueur** : « Mon DPS est-il bon ? Mon nouvel arc a-t-il vraiment aidé ? »
- **Ce que fait l'agent** : après une session, DPS moyen, part du familier, sorts les plus
  utiles ; comparaison avant / après un changement d'équipement ou de talents (lien avec les
  instantanés de stats) ; écart avec le DPS théorique calculé par `gear`.
- **Données** : **à sonder puis ajouter** : `C_DamageMeter.IsDamageMeterAvailable`,
  `GetAvailableCombatSessions`, `GetCombatSessionFromType` (présents, jamais testés). Capture
  **hors combat** (`PLAYER_REGEN_ENABLED`), résumé compact. Le journal de combat est absent du
  client : c'est la seule voie.
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : aucune donnée de combat réelle.
- **Effort** : M-L (API inconnue dans Forever).
- **Risques** : API peut-être restreinte ; ne jamais lire pendant le combat.

### 10. Groupe et guilde — valeur moyenne, effort L

- **Problème du joueur** : « Quelles quêtes du donjon on a en commun ? », « Qui dans la guilde
  fabrique cet objet ? »
- **Ce que fait l'agent** : quêtes partagées et manquantes du groupe avant un donjon ; artisans
  de la guilde pour une recette.
- **Données** : capturé (`group`) ; **à ajouter** : échange des IDs de quêtes entre membres qui
  ont ForeverScribe (`C_ChatInfo.RegisterAddonMessagePrefix` + `SendAddonMessage`, hors combat,
  sur demande) ; recettes de guilde via `C_GuildInfo.QueryGuildMembersForRecipe` (à sonder).
- **Pourquoi ChatGPT/Gemini ne peuvent pas** : aucune donnée sur les autres joueurs.
- **Effort** : L (protocole, et utile seulement si plusieurs membres ont l'addon).
- **Risques** : vie privée des autres joueurs → données de groupe jamais écrites dans le dépôt,
  durée de conservation courte ; pas de message automatique en chat public.

### 11. Héritage (Legacy) à l'échelle du compte — valeur moyenne, effort L

- **Problème du joueur** : « Quel reroll me rapporte le plus de points d'Héritage ? Où en suis-je
  de la piste (monture à 55 points) ? »
- **Ce que fait l'agent** : points du compte, points dépensés par perso (16 au plus), prochaines
  récompenses, activités qui en donnent.
- **Données** : **inconnues** : `C_PerksActivities.*`, interface `LegacySystemFrame` ; à sonder
  avec ForeverProbe avant toute promesse.
- **Effort** : L (exploration d'API d'abord).
- **Risques** : système mal documenté, chiffres « probables » seulement.

---

## Ce que j'écarte

- **Verrous de raid par perso** (« qui est encore libre pour Onyxia cette semaine ») : utile,
  mais `GetSavedInstanceInfo` est absent du client. À reprendre si une sonde trouve un
  équivalent.
- **Coach en combat, rotation en temps réel, alertes sonores** : interdit (rien en combat) et
  impossible (l'agent ne parle pas au jeu).
- **Recherche HV ou achat automatiques, achat-revente à grande échelle** : automatisation
  interdite ; rien au-delà de la lecture de ce que le joueur affiche.
- **Prévisions de prix ou « bons plans » spéculatifs** : peu fiables avec des prix partiels.
- **Actualité, guides généraux** : ChatGPT est déjà aussi bon ; le gain serait nul.

## Les 3 idées à faire en premier

1. **Plan de campagne vers une échéance (idée 3), avec le journal de session (idée 2) comme
   socle.** Les raids ouvrent le 9 décembre, dans trois semaines : c'est la question que tous
   les joueurs avancés se posent maintenant. Le journal de session est la seule brique d'addon
   vraiment nouvelle et nourrit aussi les idées 6 et 8. C'est exactement ce que ChatGPT ne peut
   pas faire (rythme réel, quêtes faites, or).
2. **Circuit de session optimisé (idée 1).** Il prolonge notre meilleure note (C01 « je fais
   quoi ? ») en plan d'action complet. Presque toutes les données sont là ; il ne manque que les
   vols connus (`C_TaxiMap`, une capture simple). Effet visible dès la première soirée.
3. **Prix de l'hôtel des ventes (idée 5), livré avec l'inventaire de compte (idée 4).** C'est le
   trou le plus net pour les joueurs avancés : aucune source de prix Forever n'existe ailleurs.
   L'inventaire de compte (sacs et banque déjà capturés) donne tout de suite un « que vaut tout
   ce que je possède et quoi vendre », puis devient le moteur des objectifs d'or de l'idée 3.

En parallèle, à coût faible : la check-list « avant de partir » (idée 6), qui réutilise ce que
`overview` calcule déjà.
