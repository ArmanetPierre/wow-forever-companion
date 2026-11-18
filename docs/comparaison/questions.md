# Comparatif : les 12 questions vitrines

Tirées de `docs/evals/banque-questions.md` (id d'origine entre parenthèses). Références vérifiées
le 18/11/2026. Perso fictif **Brannok** : ses valeurs reprennent un vrai perso capturé par l'addon.

## Contexte B (à coller avant chaque question en condition B)

> Contexte : je joue à World of Warcraft: Forever (sorti le 4 novembre 2026), région EU, client
> en français, ruleset JcJ. Mon perso : Brannok, Nain Chasseur niveau 25, Alliance, actuellement
> aux Paluns. Il me manque 6 912 XP pour le niveau 26. Arme à distance : Fusil à canon double
> (13,3 DPS) ; ma compétence Arbalètes est à 1/125. Familier : un félin niveau 24, loyauté
> Meilleur ami, heureux, 44 points de dressage libres sur 120 ; il mange viande et poisson. Dans
> mes sacs : Poisson-lune sauté ×10, Foie de Broche-tripes ×6, et pour une quête (Goulash des
> Carmines) : Chair croustillante d'araignée, Groin de grand Broche-tripes, Viande de condor
> coriace. Métiers : Travail du cuir 106, Dépeçage 141, Cuisine 20. Mon journal de quêtes est
> plein : 13 quêtes terminées à rendre, dont 4 aux Paluns.

Pour les 2 questions en anglais, le contexte B est traduit (voir `prompts-a-coller.txt`).

---

## C01 — Je fais quoi maintenant ? (L01) · perso

- **A** : « Je suis niveau 25 aux Paluns sur WoW Forever, je fais quoi maintenant ? »
- **B** : contexte B + « Je fais quoi maintenant ? »
- **Référence** :
  - D'abord **rendre les quêtes terminées** (13, journal plein) : c'est de l'XP immédiate et ça
    libère le journal. Aux Paluns, par exemple *À la recherche de l'équipe de fouilles* à
    rendre à Merrin Rockweaver `/way 38.9 52.3` ; *La chute de Dun Modr* à Longbraid le Macabre
    `/way 49.8 18.3`.
  - Ensuite des quêtes à son niveau dans la zone : *La vengeance d'Ormer* (Ormer Ironbraid,
    `/way 38.2 50.9`, niv. 24), *Découverte du passé* (Prospecteur Whelgar, `/way 38.8 52.4`,
    niv. 28, requis 25).
  - Au niveau 26 : passer chez le maître de classe.
  - Source : capture du perso, QuestieDB (coordonnées en % de la carte des Paluns).
- **Piège** : parcours générique Classic (« va aux Carmines / Loch Modan ») sans tenir compte du
  journal plein ni des quêtes à rendre.

## C02 — Arbalète ou fusil ? (E01) · perso

- **A** : « Nain chasseur 25 sur WoW Forever : j'ai loot une Arbalète de poing dissimulée, je la
  mets à la place de mon Fusil à canon double ? »
- **B** : contexte B + « J'ai loot une Arbalète de poing dissimulée (15,2 DPS, +12 puissance
  d'attaque à distance, niveau 26 requis), je la mets à la place de mon fusil ? »
- **Référence** :
  - **Pas encore** : niveau 26 requis.
  - Ensuite environ **+2,4 DPS à distance** (≈ +5,6 %) : 15,2 DPS d'arme + 12 PA à distance
    contre 13,3 DPS + 3 Agi et 3 For.
  - **Compétence Arbalètes à 1/125** : les compétences d'armes existent dans Forever ; avec 1/125
    beaucoup de tirs ratent, il faut la monter avant que le gain soit réel.
  - Dans Forever, les **bonus raciaux d'armes sont supprimés** : l'argument « les nains ont un
    bonus aux fusils » (Classic) ne tient plus.
  - 14 PA = 1 DPS (confirmé dans Forever).
- **Piège** : « garde le fusil, bonus racial nain » (Classic, faux dans Forever) ; ignorer le
  niveau requis ou la compétence d'arme.

## C03 — Découverte du passé (quête) · perso

- **A** : « Sur WoW Forever, quête Découverte du passé aux Paluns : je trouve pas les fragments
  de tablette, ils sont où ? »
- **B** : contexte B + même question.
- **Référence** (QuestieDB, id 299, niv. 28, requis 25) :
  - Donneur et receveur : Prospecteur Whelgar, `/way 38.8 52.4`.
  - 4 fragments dans l'Excavation (site de fouilles) : **Ados** dans une Relique ancienne
    `/way 34.1 49.9` ; **Modr** Relique ancienne `/way 34.3 45.7` ; **Golm** Relique ancienne
    `/way 35.5 46.2` ; **Neru** dans une Terre meuble `/way 33.1 46.4`.
  - Les fragments sont des objets à cliquer au sol, pas un butin de monstre.
- **Piège** : inventer des monstres qui lâchent les fragments, ou des coordonnées.

## C04 — Nourriture et points de dressage du familier (F01 + F02) · perso

- **A** : « Chasseur 25 sur WoW Forever, mon félin : je lui donne quoi à manger et je mets où
  mes points de dressage ? »
- **B** : contexte B + même question.
- **Référence** :
  - Félin = viande et poisson. **Poisson-lune sauté** convient. Le Foie de Broche-tripes
    (niv. 12) est trop bas pour un familier 24 (règle Classic, à vérifier dans Forever).
  - **Ne pas donner** les ingrédients gardés pour la quête *Goulash des Carmines*.
  - Il est déjà heureux et Meilleur ami (loyauté max).
  - Points de dressage = niveau × (loyauté − 1) = 24 × 5 = 120 ; **44 libres**. Les dépenser chez
    le maître des familiers (techniques apprises en jeu ou par d'autres bêtes), au choix du
    joueur ; un conseil concret (rang de Griffe/Morsure, Endurance) est acceptable s'il ne
    dépasse pas 44 points.
- **Piège** : proposer une nourriture que le félin ne mange pas (pain, fruits), ou donner les
  objets de quête ; inventer une formule de points de dressage.

## C05 — XP des donjons depuis le correctif (L02) · Forever

- **A** : « Ça vaut encore le coup d'enchaîner les donjons pour monter sur WoW Forever depuis le
  hotfix ? »
- **B** : contexte B + même question.
- **Référence** (Method, 14/11/2026 ; forum Blizzard US) — **probable** :
  - Les monstres de donjon rapportent **beaucoup moins qu'en Classic**, même après **+50 % le
    9/11/2026**.
  - Les **quêtes de donjon paient bien plus** qu'en Classic : les prendre toutes avant d'y aller.
  - Enchaîner le même donjon sans quêtes est peu rentable.
  - Un membre nettement plus haut que les monstres = **0 XP pour tout le groupe** (pas de carry).
- **Piège** : « spam donjon comme en Classic ».

## C06 — Krol'dok (D04) · Forever

- **A** : « Krol'dok sur WoW Forever, c'est où et c'est pour quel niveau ? »
- **B** : contexte B + même question.
- **Référence** :
  - **Bastion Krol'dok** (Krol'dok Stronghold), nouveau donjon à 5 de Forever.
  - Zone : **Rives Claires** (Riverglades), nouvelle zone de Forever.
  - Niveaux **40-45** (corrigé ; 40-55 au départ). Entrée exacte non publiée.
  - Pour un niveau 25 : trop tôt.
  - Source : Method (liste des donjons par niveau), warcraft.wiki.gg.
- **Piège** : le confondre avec un lieu de Classic ou inventer une entrée.

## C07 — Les raids du 9 décembre (D06) · Forever

- **A** : « Les raids du 9 décembre sur WoW Forever, c'est lesquels et faut une harmonisation ? »
- **B** : contexte B + même question.
- **Référence** (article Blizzard 24303009) — **confirmé** :
  - Ouverture le **09/12/2026**, niveau 60 : **Barrow Deeps** (10, nouveau, mont Hyjal),
    **Sommet d'Hyjal** (20, nouveau), **Repaire d'Onyxia** (40).
  - **Harmonisation d'Onyxia par personnage** : Amulette drakefeu, chaîne de faction (Alliance :
    départ Helendis Riverhorn, Steppes ardentes, `/way 85.8 69.0` selon QuestieDB ; Horde : seigneur
    de guerre Goretooth, Terres ingrates).
  - **Cœur du Magma : pas annoncé** pour le 9/12.
- **Piège** : annoncer le Cœur du Magma, ou les raids Classic (Cœur du Magma, BWL).

## C08 — GDKP (O04) · Forever

- **A** : « Les GDKP sont interdits sur WoW Forever ? »
- **B** : contexte B + même question.
- **Référence** — **confirmé** (relais presse d'un Q&R des développeurs du 17/09/2026 : Icy Veins,
  GamesRadar, Warcraft Tavern) :
  - **Oui, interdits** dans Forever (NA et EU ; la Corée serait exemptée selon Inven, probable).
  - Les loots « HR » (hard reserve) ne sont pas visés par l'annonce.
  - Achat d'or : sanctions de la suppression de l'or au bannissement.
- **Piège** : répondre avec la politique de Classic Era / Season of Discovery sans source Forever.

## C09 — Normal et JcJ dans le même donjon (P04) · Forever

- **A** : « Je joue avec mon pote qui est en Normal et moi en PvP sur WoW Forever, on peut faire
  un donjon ensemble ? »
- **B** : contexte B + « Mon pote joue sur le ruleset Normal, on peut faire un donjon ensemble ? »
- **Référence** (article Blizzard 24302070) — **confirmé** :
  - **Non** : groupe, donjons et raids seulement dans le **même ruleset**.
  - Seuls les **champs de bataille** mélangent les rulesets (sauf Hardcore).
  - **Pas de changement de ruleset** : il faut créer un perso sur le ruleset de l'autre.
- **Piège** : dire oui (comme entre royaumes connectés), ou proposer un transfert.

## C10 — Éolides : classes et départ (X02) · Forever

- **A** : « Les Éolides sur WoW Forever, c'est quelles classes et ils commencent où ? »
- **B** : contexte B + même question.
- **Référence** (Blizzard FR, warcraft.wiki.gg) — **confirmé** :
  - **Éolides = Skyborne**, la nouvelle race, qui choisit sa faction à la création.
  - Classes : **druide, chasseur, voleur, guerrier**, plus **mage (Alliance)** ou **chaman
    (Horde)**.
  - Départ sur l'**île de Zéphras** (niveaux 1-12).
  - Race liée au pack héroïque des Éolides (ou édition supérieure).
- **Piège** : liste unique sans la différence de faction ; inventer une zone de départ.

## C11 — Drowned City entrance (D03) · Forever · EN

- **A** : "Where is the Drowned City entrance in WoW Forever? I'm swimming around Grom'gol"
- **B** : English context B + same question.
- **Référence** :
  - **The Drowned City** (Cité submergée), new 5-player dungeon, **levels 35-40**, Stranglethorn
    Vale.
  - **Underwater** entrance off the coast, near `/way 21.4 27.9` (beta guide, **likely**).
  - At level 25 it's too early.
- **Piège** : invent a landmark or a boss count; claim certainty on the coordinates.

## C12 — Onyxia attunement account-wide? (D07) · Forever · EN

- **A** : "Is the Onyxia attunement account-wide in WoW Forever?"
- **B** : English context B + same question.
- **Référence** (Blizzard article 24303009) — **confirmed** :
  - **No, per character**: each character must earn the **Drakefire Amulet** (keeping it in the
    bags is enough).
  - Faction chain: Alliance ~10 steps (starts with Helendis Riverhorn, Burning Steppes), Horde ~12
    steps (Warlord Goretooth, Badlands), ending with General Drakkisath (Upper Blackrock Spire).
  - Level 60 raid, opens 9 December 2026.
- **Piège** : assume a retail-style account-wide unlock.
