# Réponses du compagnon (CMP)

Produites le 18/11/2026 avec le plugin 0.9.0 (serveur MCP `forever`, voix `joueur`) et la base
locale construite depuis le client 1.60.1.70938 + QuestieDB (révision e1652ce621). Perso réel
anonymisé en **Brannok** (Nain Chasseur 25, Alliance, JcJ, Les Paluns ; capture vieille de ~15 h).

Méthode : l'agent suit `agents/forever-guide.md`, `knowledge/regles-forever.md`, `voix.md` et la
skill concernée, et appelle les outils via `docs/evals/outil.py`. Le compagnon ne reçoit pas le
contexte B : il lit le perso par l'addon. « Temps outils » = temps des appels au serveur ; le
temps de génération du modèle n'est pas compté.

Pour le juge à l'aveugle : retirer les badges `[Forever · …]`, « capture », « Ctrl+Maj+S » et
les noms d'outils (voir `protocole.md`).

---

## C01 — Je fais quoi maintenant ?

**Appels :** `overview {"perso":"Brannok"}` (1 appel) · **Temps outils :** 0,30 s · Web : 0

**Rends tes 13 quêtes terminées avant tout : ton journal est plein.**
- Aux Paluns, 4 à rendre : *À la recherche de l'équipe de fouilles* chez Merrin Rockweaver
  `/way 38.9 52.3`, *La chute de Dun Modr* chez Longbraid le Macabre `/way 49.8 18.3`,
  *Récupération de marchandises* sur la Caisse endommagée `/way 13.5 41.4`, et *Fleur des cieux*.
- Ensuite, deux quêtes à ton niveau juste à côté : *La vengeance d'Ormer* (Ormer Ironbraid
  `/way 38.2 50.9`) et *Découverte du passé* (Prospecteur Whelgar `/way 38.8 52.4`, requis 25).
- Il te manque 6 912 XP pour le 26 ; au 26, passe chez ton maître de classe.
- Ton Dépeçage est à 141/150 : prends le rang suivant chez le formateur en ville.

_Données du perso et QuestieDB · capture d'il y a 15 h, Ctrl+Maj+S en jeu pour actualiser._

## C02 — Arbalète ou fusil ?

**Appels :** `gear {"perso":"Brannok","objet":"Arbalète de poing dissimulée"}` (1 appel) ·
**Temps outils :** 0,11 s · Web : 0

**Pas encore : elle demande le niveau 26, et ensuite c'est environ +2,4 DPS (+5,6 %).**
- Fusil à canon double 13,3 DPS (+3 Agi, +3 For) contre arbalète 15,2 DPS (+12 PA à distance) :
  43,1 → ≈ 45,5 DPS à distance en coups blancs.
- Le vrai frein : ta compétence **Arbalètes est à 1/125**. Les compétences d'armes existent dans
  Forever, tu vas rater pas mal de tirs au début. Monte-la sur des mobs verts avant de la sortir
  sur un élite.
- Pas de regret côté nain : les bonus raciaux d'armes ont sauté dans Forever, le fusil ne te
  donne aucun bonus caché.

_Base locale Forever · sûr (14 PA = 1 DPS confirmé en jeu) ; le malus de compétence basse est la
règle Classic, probable dans Forever._

## C03 — Découverte du passé : où sont les fragments ?

**Appels :** `quests {"perso":"Brannok","quete":"Découverte du passé"}` (1 appel) ·
**Temps outils :** 0,12 s · Web : 0

**Les 4 fragments sont à ramasser au sol dans l'Excavation, à l'ouest de Whelgar.**
- **Ados** : dans une Relique ancienne, `/way 34.1 49.9`
- **Modr** : Relique ancienne, `/way 34.3 45.7`
- **Golm** : Relique ancienne, `/way 35.5 46.2`
- **Neru** : dans une Terre meuble, `/way 33.1 46.4`
- Tu rends tout au Prospecteur Whelgar, `/way 38.8 52.4`. Quête 28, requis 25 : le site est
  plein de mobs de ton niveau ou plus, pull un par un.

_QuestieDB · positions en % de la carte des Paluns ; une quête retouchée par Forever peut
différer, vérifie en jeu si un point ne colle pas._

## C04 — Nourriture et points de dressage du familier

**Appels :** `pet {"perso":"Brannok"}` (1 appel) · **Temps outils :** 0,11 s · Web : 0

**Ton félin est déjà heureux et au max de loyauté : continue au Poisson-lune sauté, et tu as 44
points de dressage à placer.**
- Il mange viande et poisson. Tes 10 Poisson-lune sauté sont parfaits. Le Foie de Broche-tripes
  (niv. 12) est trop bas pour un familier 24, il ne le contentera presque plus.
- Ne lui donne surtout pas la Chair croustillante d'araignée, le Groin de grand Broche-tripes ni
  la Viande de condor coriace : c'est pour ta *Goulash des Carmines*.
- Points de dressage : 24 × (6 − 1) = 120 au total, 44 libres. Tu as Griffe 3 et Morsure 2 :
  le prochain rang de Morsure ou de Griffe chez le maître des familiers est le plus rentable en
  dégâts, à condition de l'avoir appris sur une bête.

_Données du perso · sûr ; formule des points confirmée sur une capture Forever ; règle de la
nourriture trop basse : [Classic], à vérifier en jeu._

## C05 — XP des donjons depuis le correctif

**Appels :** `search {"texte":"XP donjons","type":"connaissance"}` puis ouverture de la section
« XP des donjons » (2 appels) · **Temps outils :** 0,25 s · Web : 0

**Spammer le même donjon, non ; y aller avec toutes ses quêtes, oui.**
- Les mobs de donjon rapportent bien moins qu'en Classic, même après le **+50 % du 9/11**.
- Les quêtes de donjon, elles, paient beaucoup plus : *Deviate Hides* passe de 1 600 XP en
  Classic à 3 100 dans Forever. Ramasse-les toutes avant d'entrer.
- Pas de carry par un 60 : si un membre est nettement au-dessus du niveau des mobs, **personne**
  ne gagne d'XP.
- À ton niveau : les Excavations des Paluns (24-29) sont juste à côté, avec leurs quêtes.

_[Forever] Method, 14/11/2026 · probable ; le débat est encore vif sur le forum, ça peut bouger._

## C06 — Krol'dok

**Appels :** `dungeon {"donjon":"Bastion Krol'dok","perso":"Brannok"}` (1 appel) ·
**Temps outils :** 0,11 s · Web : 0

**Bastion Krol'dok, dans les Rives Claires, pour les niveaux 40-45 : trop tôt pour toi.**
- C'est un des 9 nouveaux donjons de Forever, dans une zone qui n'existait pas en Classic
  (Riverglades).
- La fourchette a été corrigée à 40-45 (elle était annoncée 40-55).
- L'entrée exacte n'est pas encore publiée : on regardera quand tu approcheras du 40.

_Base locale Forever + [Forever] Method et warcraft.wiki.gg · sûr pour les niveaux, entrée
inconnue._

## C07 — Les raids du 9 décembre

**Appels :** `dungeon {"donjon":"Onyxia","perso":"Brannok"}` (1 appel) · **Temps outils :**
0,16 s · Web : 0

**Trois raids niveau 60 le 9/12 : Barrow Deeps (10), Sommet d'Hyjal (20) et Onyxia (40), et
seule Onyxia demande une harmonisation, par perso.**
- Barrow Deeps et Hyjal sont nouveaux, tous les deux au mont Hyjal.
- Onyxia : il te faut l'**Amulette drakefeu** dans les sacs. Côté Alliance, ~10 étapes, départ
  avec *La menace des draconiens* chez Helendis Riverhorn, Steppes ardentes `/way 85.8 69.0`
  (requis 48), fin au sommet du pic Rochenoire.
- Le Cœur du Magma n'est **pas** annoncé pour le 9/12.
- À ton niveau 25, garde ça pour plus tard.

_[Forever] annonce Blizzard · sûr ; chaîne d'harmonisation : QuestieDB._

## C08 — GDKP

**Appels :** `search {"texte":"GDKP","type":"connaissance"}` (1 appel) · **Temps outils :**
0,11 s · Web : 0

**Oui, les GDKP sont interdits dans Forever.**
- Annoncé par les développeurs au Q&R du 17/09/2026 (relayé par Icy Veins, GamesRadar, Warcraft
  Tavern) : ça vise l'Amérique du Nord et l'Europe, donc ton serveur EU.
- Les raids en « HR » (hard reserve) ne sont pas concernés par l'annonce.
- L'achat d'or est puni sévèrement : de la suppression de l'or jusqu'au ban définitif.

_[Forever] relais presse d'une déclaration des développeurs · sûr ; le texte Blizzard original
n'a pas été lu._

## C09 — Normal et JcJ dans le même donjon

**Appels :** `search {"texte":"ruleset groupe donjon","type":"connaissance"}` puis ouverture de
la section « Rulesets » (2 appels) · **Temps outils :** 0,23 s · Web : 0

**Non : dans Forever, on ne groupe qu'avec des joueurs du même ruleset.**
- Donjons et raids, c'est même ruleset obligatoire. Ton pote en Normal et toi en JcJ, c'est mort.
- Seuls les champs de bataille mélangent les rulesets (sauf Hardcore).
- Pas de transfert possible entre rulesets : l'un de vous deux doit monter un perso sur le
  ruleset de l'autre. Attention, en JcJ c'est une seule faction par compte.

_[Forever] annonce Blizzard sur les rulesets · sûr._

## C10 — Éolides : classes et départ

**Appels :** `search {"texte":"Éolides classes","type":"connaissance"}` puis ouverture de la
section « Éolides » (2 appels) · **Temps outils :** 0,22 s · Web : 0

**Les Éolides (Skyborne) peuvent être druide, chasseur, voleur ou guerrier, plus mage côté
Alliance ou chaman côté Horde, et commencent sur l'île de Zéphras.**
- La faction se choisit à la création ; l'île de Zéphras couvre les niveaux 1 à 12.
- Racial phare : *Walk on Air*, un vol plané d'environ 10 s qui évite les dégâts de chute (nom
  français pas encore confirmé).
- Il faut le pack héroïque des Éolides ou une édition supérieure.

_[Forever] Blizzard FR et warcraft.wiki.gg · sûr pour les classes et le départ ; détails des
raciaux probables._

## C11 — Drowned City entrance (EN)

**Calls:** `dungeon {"donjon":"Drowned City","perso":"Brannok","lang":"en"}` (1 call) ·
**Tool time:** 0.11 s · Web: 0

**It's underwater off the Stranglethorn coast, around /way 21.4 27.9, but at 25 you're ten
levels early: it's a 35-40 dungeon.**
- The Drowned City (Cité submergée in the French client) is one of Forever's 9 new 5-player
  dungeons.
- The coordinates come from a beta guide: treat them as likely, not certain.
- Come back around 35; at 25 the mobs on the way will flatten you.

_[Forever] local DB + beta guide · likely for the entrance, sure for the level range._

## C12 — Onyxia attunement account-wide? (EN)

**Calls:** `search {"texte":"Onyxia attunement","type":"connaissance","lang":"en"}` (1 call) ·
**Tool time:** 0.11 s · Web: 0

**No, it's per character: every character needs its own Drakefire Amulet.**
- Keeping the amulet in your bags is enough to enter Onyxia's Lair (40-player, level 60, opens
  9 December 2026).
- Alliance chain: about 10 steps, starting with Helendis Riverhorn in the Burning Steppes and
  ending with General Drakkisath at the top of Blackrock Spire. Horde: about 12 steps, starting
  with Warlord Goretooth in the Badlands.
- Blizzard's advice: start early, the chain has elite quests and several high-level dungeons.

_[Forever] Blizzard raid announcement · confirmed._

---

## Récapitulatif

| Question | Appels | Temps outils | Web |
|---|---:|---:|---:|
| C01 | 1 | 0,30 s | 0 |
| C02 | 1 | 0,11 s | 0 |
| C03 | 1 | 0,12 s | 0 |
| C04 | 1 | 0,11 s | 0 |
| C05 | 2 | 0,25 s | 0 |
| C06 | 1 | 0,11 s | 0 |
| C07 | 1 | 0,16 s | 0 |
| C08 | 1 | 0,11 s | 0 |
| C09 | 2 | 0,23 s | 0 |
| C10 | 2 | 0,22 s | 0 |
| C11 | 1 | 0,11 s | 0 |
| C12 | 1 | 0,11 s | 0 |
| **Total** | **15** | **≈ 1,9 s** | **0** |
