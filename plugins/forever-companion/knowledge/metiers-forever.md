# WoW Forever — métiers : nouveautés et changements

> Fiche établie le 18/11/2026 (jeu sorti le 04/11/2026). Chaque fait porte son badge, sa certitude et sa source.
> Complète la section « Métiers » de `forever-essentiels.md` (bonus de campement, potions en Secourisme).
> **Base locale** = `forever-frFR.sqlite` construite depuis les fichiers du client Forever et ses correctifs
> (`origin` : `client` = fichiers du jeu, `modifie` = modifié par un correctif Forever). Attention : le client
> contient aussi du contenu inactif (p. ex. recettes « obsidienne » ou « Boîte bricolée » héritées de Season of
> Discovery) ; une recette présente dans la base n'est donc pas forcément obtenable. Les rangs de recette de la
> base sont souvent estimés (« ≈ »).
> Abréviations des sources :
> - **[BLZ-CAMP]** https://news.blizzard.com/en-us/article/24301516 (officiel, « Gather Around the Campfire », avant la sortie, non daté sur la page)
> - **[HOTFIX]** https://us.forums.blizzard.com/en/wow/t/2403040 (fil officiel des correctifs Forever, entrées du 05/11 au 17/11/2026)
> - **[WIKI-CAMP]** https://warcraft.wiki.gg/wiki/Camping (modifiée le 17/11/2026)
> - **[WIKI-RBOT]** https://warcraft.wiki.gg/wiki/Reagent_Bot et https://warcraft.wiki.gg/wiki/Repair_Bot_(Camping) (modifiées le 03/11/2026, patch 1.60.1)
> - **[WIKI-MF]** https://warcraft.wiki.gg/wiki/Merchant's_Favor (modifiée le 20/10/2026)
> - **[WIKI-LEGACY]** https://warcraft.wiki.gg/wiki/Legacy_System (modifiée le 15/11/2026)
> - **[METHOD-REP]** https://www.method.gg/wow-forever/azerorth-commerce-authority-and-durotar-supply-and-logistics-reputation-guide (03/11/2026)
> - **[WOWGG-ING]** https://wow.gg/professions/forever/engineering (mise à jour le 08/11/2026)
> - **[BW-FA]** https://blizzardwatch.com/2026/10/16/first-aid-getting-new-recipes-updates-world-warcraft-forever/ (16/10/2026, bêta)
> - **[FR-MF]** https://kami-labs.fr/faveur-marchande-wow-forever/ · https://gamewave.fr/world-of-warcraft-forever/wow-forever-faveur-marchande-comment-obtenir-cette-monnaie/ (noms FR, novembre 2026)
> - **[ING-SPE]** https://www.warcrafttavern.com/forever/guides/engineering/ (403, extrait) · https://www.gfinityesports.com/article/world-of-warcraft-forever-engineering-guide-1-300-leveling-trainers · https://overgear.com/guides/wow-forever/engineering-overview/ (guides, novembre 2026)
> - **[BASE]** base locale Forever (lecture du 18/11/2026)

## Ingénierie Forever : Robot vendeur de composants (Reagent Bot), Robot réparateur (Repair Bot), Établi d'anarchiste

- **Robot vendeur de composants** (EN : *Reagent Bot*) : objet de campement d'ingénierie, rang **20**, appris chez le **formateur**. Composants : 1 Poignée de boulons en cuivre + 1 Tube en cuivre. Posé près d'un feu de camp, il invoque un robot qui **vend des composants** au poseur et aux joueurs proches. [Forever · base locale] (recette 1230656, objet 279950, ingénierie 20, `modifie`) + [Forever · sûr] [BLZ-CAMP] [WIKI-RBOT]. **Certitude haute.**
- **Robot réparateur** (EN : *Repair Bot*, à ne pas confondre avec le Robot réparateur 74A de Classic, rang 300) : rang **140**. Composants : 2 Bidules bourdonnants en bronze + 1 Tube en bronze + 1 Cuir lourd. Le robot **vend des composants et répare** l'équipement ; il peut remplacer un Robot vendeur de composants déjà posé. [Forever · base locale] (recette 1263034, objet 279949, rang 140 ; plan « Plan : robot réparateur » 273092) + [WIKI-RBOT]. **Certitude haute.**
  - Source du plan : **Sneed (Mortemines)** selon le wiki [WIKI-RBOT] [WIKI-CAMP] → **probable**. wow.gg indique un vendeur « Happy Camper » à Dun Morogh [WOWGG-ING] : **non confirmé** (absent du wiki et de la base locale).
- **Établi d'anarchiste** : palier 3 du campement d'ingénierie, rang **300**, composants Essence d'anarchie + 2 Rouages en thorium ; plan sur **Ezra Grimm (Stratholme)**. [Forever · base locale] (recette 1263083, objet 279989) + [WIKI-CAMP]. **Probable** (effet non décrit).
- Les objets de campement partagent un **temps de recharge de 1 h**. [BLZ-CAMP] [WIKI-RBOT] **Sûr.**
- **Paliers de formateur** (Forever) : Apprenti → 75, Compagnon (50 de compétence, niv. 10) → 150, Expert (125, niv. 20) → 225, Artisan (200, niv. 35) → 300. Formateurs Artisan : Buzzek Bracketswing (Tanaris), Kaylaena Springwhisper (mont Hyjal) ; un formateur de base sur l'île de Zéphras (« Strange Hermit »). [Forever · probable] [WOWGG-ING] [ING-SPE] (guides, 08/11/2026).
- **Spécialisations gnome / gobelin** : toujours présentes, à **200** de compétence et niveau 30, selon plusieurs guides [ING-SPE]. **Probable.** Le bonus racial gnome n'est plus +15 en ingénierie : les appareils des gnomes ratent 20 % moins souvent (voir `forever-essentiels.md`). **Probable.**
- Correctif du 10/11/2026 : prix marchand de la Grenade en fer baissé à 1 pa 25 pc (au lieu de 5 pa) ; *Swiftstrike Shot* (FR client probable : Munitions de frappe rapide) et *Swiftfeather Arrow* (Flèche plumevive) ne sont plus liés quand ramassés (munitions des raids, pas encore disponibles). [Forever · sûr] [HOTFIX]
- Dans la base locale, les munitions de raid sont des recettes d'ingénierie ≈ 325 : **Flèche plumevive** et **Munitions de frappe rapide** (barres de thorium lourd). [Forever · base locale] **Probable** (disponibles avec les raids du 09/12).

## Faveur des marchands (Merchant's Favor), caisses détournées, Fritz Féplouf (Fritz Fizzle) et Fizzlefuse

- **Faveur marchande** (EN : *Merchant's Favor* ; FR vu aussi : « Faveur du marchand ») : **monnaie propre à Forever**, gagnée en remplissant des **caisses** trouvées dans le monde (FR client : « Caisse détournée », EN : *Waylaid Crate*) puis en les rendant au camp de sa faction contre Faveur et réputation. [Forever · sûr] [WIKI-MF] [METHOD-REP] ; nom FR de la monnaie **probable** [FR-MF] (non présent dans la base locale).
  - Une caisse ne demande **qu'un** des objets de sa liste ; la première remise donne une étiquette d'expédition qui lance une quête à 50 Faveur. Caisses et *Craftsman's Writs* (FR client : « Commission d'artisan ») tombent sur les monstres, **aussi en donjon** depuis le 09/11. [METHOD-REP] [HOTFIX] **Probable / sûr pour le donjon.**
  - Les caisses s'achètent aussi à l'hôtel des ventes. [METHOD-REP] **Probable.**
- **Camps** : Alliance, **Administration commerciale d'Azeroth** (*Azeroth Commerce Authority*) aux **Trois chemins, Les Carmines** (≈ 10, 73) ; Horde, **Transports et logistique de Durotar** (*Durotar Supply and Logistics*) à l'ouest de la **Croisée, Tarides** (≈ 42, 34). Remise des caisses : Marcy Baker (FR client : **Marcy Fournier**, « Récupération d'inventaire ») / Dokimi. [WIKI-MF] [METHOD-REP] + [Forever · base locale] (PNJ 256390). **Sûr.**
- **Vendeurs** : un par métier d'artisanat (+ cuisine), qui vend des recettes et une « certification » de métier (1 000 Faveur, métier à 300). Alliance (noms FR de la base locale) : Nina Feucertain (alchimie), Stondry Sombremartel (forge), Kalsey Sanden (cuisine), Alynsia (enchantement), **Fritz Féplouf (ingénierie, EN *Fritz Fizzle*)**, Daniel Chantepoint (cuir), Mivin Tissombre (couture), Huey Valradieux (mules), Tamelyn Aldridge (tabard, mascotte, jouet). Horde : **Fizzlefuse** (ingénierie), Apothecary Durelle, Jim'bek, Beneris, Pawani, Gor'mak, Aza'bek, Okamache, Gishah. [METHOD-REP] [WOWGG-ING] + [Forever · base locale] (PNJ 256729-256742, sous-titres de métier). **Sûr** pour l'existence ; noms Horde **probables** (absents de la base locale).
- **Prix** : recettes de 30 à 360 Faveur selon le rang ; Rênes de kodo de bât 6 000 (exalté), Friandise de mule de bât 1 500 (révéré), jouet « Advertising License Application » 1 200 (honoré), tabard 200 (exalté). [WIKI-MF] [METHOD-REP] **Probable** (guides de lancement).
- **Schémas d'ingénierie vendus par Fritz Féplouf / Fizzlefuse** (rang requis · prix en Faveur, [WOWGG-ING], croisés avec la base locale, noms FR) :
  - 25-145 · 45 : Languette SUR-T, Dynamite SUR-T, Bombe en cuivre SUR-T, Sacoche de bombes en cuivre, Emballage Ev-Lan, Bombe en cuivre XL Ev-Lan, Rembourrage antidérapant SUR-T.
  - 165-200 · 180 : Sacoche de bombes en bronze, Baudrier fantaisiste, Ceinturon à gadgets, Corde cliquetante, Cloche SUR-T, Mèche ignifugée Ev-Lan, Lunettes molles / tordues / à bouton cassé / cabossées.
  - 225-285 · 270 : Cape d'urgence de terrain, Porte-créature compact, Sacoche de bombes en fer, Couteau de l'armée gnome, Parachute jetable SUR-T, Plumerang (*Loot-A-Rang*), Sacoche de bombes en sombrefer.
  - 300 · 360 : Pouletisateur gnome, Batterie rechargeable super sûre, Planeur gobelin ultraléger, Camoufleur 52 ; Certification d'ingénierie 1 000.
  - « SUR-T » = *SAF-T*, « Ev-Lan » = *EZ-Thro* dans le client français. [Forever · base locale] (recettes 1266893-1266943, 1308178-1308186, 1317958-1317961). **Sûr** pour les recettes ; prix et rangs du vendeur **probables**.

## Campement : objets de campement par métier (paliers 20 / 140 / 300)

- Feu de camp de **Cuisine** obligatoire ; être **assis ou en train d'artisaner au camp 1 min** pour recevoir les bonus ; tous les objets partagent **1 h** de recharge ; bonus exclusifs avec les buffs de classe équivalents. [Forever · sûr] [BLZ-CAMP]
- Palier 1 au rang 20 (formateur ou quêtes « 101 »), paliers 2 et 3 (140 et 300) : **plans sur des boss de donjon**. [WIKI-CAMP] [BLZ-CAMP] **Sûr.**
- Tableau (noms FR et rangs de la base locale, sources des plans [WIKI-CAMP]) :

| Métier | Rang 20 | Rang 140 (plan) | Rang 300 (plan) |
|---|---|---|---|
| Ingénierie | Robot vendeur de composants | Robot réparateur (Sneed, Mortemines) | Établi d'anarchiste (Ezra Grimm, Stratholme) |
| Secourisme | Trousse de premiers soins | Étude des toxines (Commandant Springvale, Ombrecroc) | Laboratoire de médecin de peste (Dr Theolen Krastinov, Scholomance) |
| Pêche | Bocal à poisson | Râtelier de pêche (Gelihast, Profondeurs de Brassenoire) | Hutte de pêche (Jammal'an, temple d'Atal'Hakkar) |
| Forge | Meule à aiguiser | Enclume (Gilnid, Mortemines) | Forge magistrale (Argelmach, Profondeurs de Blackrock) |
| Couture | Bannière de faction | Rouet | Métier à tisser (Baronne Anastari, Stratholme) |
| Travail du cuir | Tente du camp | Râtelier de tannage (rang **125** depuis le 06/11) | Machine à coudre (Vectus, Scholomance) |
| Alchimie | Puits de mana | Fermenteur | Laboratoire d'alchimie (Ras Murmegivre, Scholomance) |
| Enchantement | Luth enchanté | Récupérateur arcanique | Forge arcanique |
| Herboristerie | Bougie d'encens | Serre | Hybrideur de graines |
| Minage | Magnétite | Jardin de pierres | Fonderie en fusion (Ambassadeur Flamelash, Profondeurs de Blackrock) |
| Dépeçage | Chaise du camp | Guide de terrain | Établi de trappeur |

  [Forever · base locale] (objets 279940-279990) **sûr** pour noms et rangs ; boss des plans **probables** [WIKI-CAMP].

## Cuisine Forever : feux de camp, thés, frappés, nouvelles recettes

- **Feux de camp** : Kit de feu de camp basique (rang 1, 3 objets de camp, feu de 60 min) → **Kit de feu de camp de compagnon** (5 objets, rang **90** depuis le correctif du 10/11, plan sur Seigneur Serpentis, cavernes des Lamentations) → **Kit de feu de camp de spécialiste** (EN *Expert*, 10 objets, plan rang 200, objet rang 220) → **Four en fer** (300, poste de cuisine). Plus **Festin de Macaron** (EN *Cookie's Feast*, rang 140, nourriture d'Endurance, plan sur Macaron aux Mortemines). [Forever · base locale] (objets 279961, 279974, 279981, 279982, 279957 ; le 279961 est `modifie`, ce qui recoupe le correctif) + [WIKI-CAMP] [HOTFIX]. **Sûr.**
- **Nouvelles recettes de cuisine** dans la base : thés (Thé de sérénité ≈ 25, Thé royal ≈ 75, Thé aux racines ≈ 125, Thé de triage ≈ 175, Thé du soleil ≈ 225, Thé des sages ≈ 275), frappés (Frappé venimeux ≈ 25 → Frappé pernicieux ≈ 275), plats de raptor, d'ours, de cerf, Omelette de petit déjeuner, Linguines aux palourdes, plats aux **Sels sacrés** ≈ 325 et festins (Grand banquet de homard). [Forever · base locale] **Probable** : présentes dans le client, effets et mode d'apprentissage non vérifiés en jeu.
- Correctif du 13/11 : Nyalah Brightfire (Valanaar, île de Zéphras) vend plus de fournitures de cuisine ; du 05/11 : Épices douces revendues 1 pc au marchand. [Forever · sûr] [HOTFIX]

## Secourisme Forever : potions de soins, cataplasmes, garrots

- Les **six potions de soins** (mineure → majeure) sont des recettes de **Secourisme**, avec des épices en plus de l'herbe et de la fiole. Rangs annoncés en bêta : 1, 55, 110, 155, 215, 275 [BW-FA] ; la base locale estime ≈ 25, 65, 110, 155, 225, 275. [Forever · base locale] (recettes 1244431-1244436) + [Forever · probable] [BW-FA]. **Sûr** pour l'existence, rangs exacts **à vérifier en jeu**.
- **Cataplasmes** (soignent les maladies jusqu'à un niveau donné : simple, rusé, excellent, puissant) et **garrots** (arrêtent les saignements : laine, cuir, chirurgical) sont nouveaux. [Forever · base locale] + [BW-FA] (rangs de bêta 90/140/210/280 et 120/200/265). **Sûr** pour l'existence.
- Objets de camp : Trousse de premiers soins (20, Endurance), **Étude des toxines** (140, distribue potions et anti-venin), **Laboratoire de médecin de peste** (300, potions et cataplasmes, plus l'effet de la trousse). [BW-FA] [WIKI-CAMP] + [Forever · base locale]. **Probable** pour les effets.

## Pêche Forever : Bocal à poisson, Râtelier de pêche, tournoi

- **Bocal à poisson** (20, +8 % de stats), **Râtelier de pêche** (140, fournit des appâts à tous depuis le 16/11 ; poissons gonflés plus fréquents), **Hutte de pêche** (300). [Forever · base locale] + [BLZ-CAMP] [HOTFIX] **Sûr.** Le Râtelier a encore des erreurs « pas de butin » connues (10/11). [HOTFIX]
- Tournoi de pêche hebdomadaire de Strangleronce : plus de gagnants par ruleset depuis le 13/11. [Forever · sûr] [HOTFIX]

## Héritage (Legacy) : perks de métiers, Marchandage, Économie des composants

- L'arbre **Métiers** de l'Héritage contient notamment **Marchandage** (EN *Bartering*, 2 rangs, baisse les prix des marchands : 5 % puis 10 % selon les guides), Heures supplémentaires (*Working Overtime*, 5 rangs), Bonus de performance (3), Cordon bleu (*Master Chef*, cuisine qui produit plus), Étude assidue. [Forever · base locale] (sorts 1225451-1225469) + [WIKI-LEGACY] ; montants **probables** (guides).
- **Économie des composants** (*Reagent Economy*, arbre Ressources) : sorts de classe sans composant acheté et objets de camp de palier 1 **gratuits** ; **Permanence** : buffs de camp 50 %/100 % plus longs ; **Guide de terrain** (arbre Aventure) : recharge des objets de camp réduite (8/17/25 %). [WIKI-CAMP] [WIKI-LEGACY] + [Forever · base locale]. **Probable.** Correctif du 17/11 : Économie des composants ne cesse plus de fonctionner au hasard. [HOTFIX]

## Économie des métiers : hôtel des ventes, prix marchands, correctifs

- Dépôt minimal à l'hôtel des ventes prévu à 1 pc (au lieu de 1 pa), **retiré** le 12/11 et reporté ; absent des correctifs du 17/11. [Forever · sûr] [HOTFIX] Ne pas l'annoncer comme appliqué.
- 10/11 : les marchands rachètent moins cher certaines armures craftées (cuir, couture, forge) ; Élixir des Arcanes mineur revendu 5 pc ; Pierre à aiguiser grossière donne des points jusqu'à 90. 11/11 : sacs de couture corrigés (Sac en tisse-mage rouge 14 places, sacs en soie 12, sacs en laine 10). 05/11 : sacs de métier d'apprenti vendus sur l'île de Zéphras. [Forever · sûr] [HOTFIX]
- Sacs de composants de métier (lin → étoffe lunaire, cuir léger) : recettes de couture et de cuir dans la base. [Forever · base locale] **Sûr** pour l'existence.

## Éléments cités par d'autres IA : vérification

- **Reagent Bot** : **confirmé** (= Robot vendeur de composants, ingénierie 20). **Repair Bot** : **confirmé** (= Robot réparateur, ingénierie 140). **Fritz Fizzle** : **confirmé** (= Fritz Féplouf, vendeur d'ingénierie de l'Administration commerciale d'Azeroth, Les Carmines). **Merchant's Favor** : **confirmé** (= Faveur marchande). Sources ci-dessus, 18/11/2026.
- Non confirmé : « Happy Camper » à Dun Morogh comme vendeur du plan Robot réparateur (wow.gg seul) ; plafond hebdomadaire de Faveur (aucune source).
