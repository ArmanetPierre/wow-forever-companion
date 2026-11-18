# Verdict C14 : « suite de quêtes optimale 25 → 30 (chasseur) »

## Notes

| Critère | R1 | R2 | R3 |
|---|---|---|---|
| 1. Justesse des faits | 0 | 2 | 0 |
| 2. Pas de confusion Classic | 1 | 2 | 1 |
| 3. Qualité du plan | 1 | 2 | 1 |
| 4. Prise en compte du perso | 1 | 2 | 1 |
| 5. Honnêteté sur l'incertitude | 1 | 2 | 0 |
| 6. Hallucinations | 0 | 2 | 0 |
| **Total /12** | **4** | **12** | **3** |

Justification des 0 :
- R1, critères 1 et 6 : « Cherche Howin Kindfeather, à l'est de Menethil ». Dans la base, ce PNJ est aux Hinterlands, niveau 45. Toute l'étape 28 → 29 repose sur une chaîne introuvable : *This Land Was Their Land*, *Razormaw Needling*, *Trying Times*, et les quêtes élites de « Dragonmaw Retreat ».
- R3, critère 1 : donjon donné « niveau 26–32 » alors que la base indique 24-29, d'où un conseil faussé (« 28 – 29 » pour y aller). R3 dit aussi de prendre *À la recherche de Lame-chantante* et de débloquer *Peaux des hautes-terres*, deux quêtes déjà dans le journal (la première est même à rendre).
- R3, critère 5 : « bonus de nourriture (+5 % d'XP sur les éliminations) » est affirmé sans source. La base ne connaît pas ce bonus : les campements donnent des bonus de métier, et la tente du travail du cuir donne du repos.
- R3, critère 6 : « quête de classe de Chasseur (disponible auprès des maîtres chasseurs en capitale) » au niveau 30. Je n'en trouve aucune trace, ni en Classic ni dans Forever. Les noms de la chaîne de Rethiel sont aussi inventés : « Piétinement, Tabou du feu, Cloques sur la terre », alors que la base donne *Piétinements de pattes*, *Feu interdit* et *Fièvre sur le pays*.

## Faits vérifiés

Sources : base = fc.py (base locale Forever + QuestieDB + guide method.gg), web = recherches citées.

### R1
- 13 quêtes à rendre, journal plein → **vrai** (base, quests a_rendre)
- « 4 quêtes terminées aux Paluns » → **faux** : il y en a 5 (Lame-chantante, équipe de fouilles, Récupération de marchandises, Fleur des cieux, Dun Modr) (base)
- Excavations des Paluns, donjon Forever, 24-29 → **vrai** (base, dungeon)
- Howin Kindfeather à l'est de Menethil → **faux** : PNJ 11810 aux Hinterlands, niveau 45 (base)
- *This Land Was Their Land*, *Razormaw Needling*, *Trying Times* → **introuvable** (base et web : https://www.warcrafttavern.com/forever/guides/excavation-site-wetlands-quests/ , https://games.gg/world-of-warcraft/guides/wow-forever-wetlands-leveling-guide/)
- *Death to the Dragonmaw*, *Forced Disarmament*, *Stopping the Cycle* (« Dragonmaw Retreat ») → **introuvable** (base, et rien sur https://warcraft.wiki.gg/wiki/Wetlands_quests ni sur Wowhead)
- Rethiel the Greenwarden aux Paluns → **vrai** (base, PNJ 1244, /way 56.4 40.4)
- Quêtes de Sombre-Comté (*The Night Watch*, *Legend of Stalvan*, *Worgen in the Woods*, *Look to the Stars*, *The Hermit*) → **vrai** (quêtes Classic conservées dans Forever)
- *Kayneth Stillwind* cité comme une quête d'Ashenvale → **faux** : c'est un PNJ (mineur)
- Ressources « Polestar 27–30 », « Hardcore Helper » → sans lien, inutilisables

### R2
- 25 → 26 : 6 912 XP, les rendus suffisent → **vrai** (base : 13 rendus ≈ 26 980 XP, estimation)
- *La chute de Dun Modr* → Longbraid le Macabre /way 49.8 18.3 → **vrai** (base)
- *La guerre contre les Sombrefer*, Motley Garmason /way 49.7 18.2 → **vrai** (base, id 303)
- Merrin Rockweaver /way 38.9 52.3 ; *La vengeance d'Ormer* /way 38.2 50.9 ; *Découverte du passé* /way 38.8 52.4 → **vrai** (base, ids 294 et 299)
- *Fiora Longears*, Jack Flint /way 10.0 58.0 → **vrai**, mais c'est une quête de niveau 20 qui envoie à Theramore : peu utile (base)
- *Lost in the Thicket Things*, Caitlin Grassman /way 11.9 58.8 ; *Cuir des hautes-terres*, James Halloran /way 8.6 55.7 (en cours) → **vrai** (base, guide method.gg)
- Donjon 24-29, groupe de 5 ; Atours de plumes bigarrées (Dent-Sombre, +1,3 DPS) ; Arme d'épaule mire-de-golem (Gardien des reliques, 16,6 DPS, niveau 28, +3,8 DPS) ; Gardien niveau 31 une fois activé → **vrai** (base, dungeon)
- Rendus de Loch Modan, Dun Morogh, Elwynn et Marche de l'Ouest avec PNJ et /way (Daryl, Stonegear, Ozzie, Paxton, Theocritus, Gryan) → **vrai** (base, journal)
- *Porté disparu*, Caporal Keeshan /way 23.3 12.6 → **vrai** (base, id 219)
- *Le viaduc de Thandol*, Rhag Garmason, requis 28 → **vrai** (base, id 631)
- *Le tord-boyaux de MacKreel*, Foggy MacKreel /way 43.2 92.6 → **vrai** (base, id 647)
- *Le long de la côte* /way 51.5 58.4 ; *Bisque de tortue apaisante* /way 51.9 58.7, requis 28 → **vrai** (base, ids 536 et 555)
- *Syndicat d'assassins* /way 48.1 59.1 → **vrai**, mais quête de niveau 33 : haute pour 28-30 (mineur)
- *Une tâche sinistre*, niveau 34 → **vrai** (base, id 304)
- Dépeçage 141/150, rang suivant disponible → **vrai** (base, professions)
- 165 000 XP de 25 à 30 → estimation Classic, présentée comme telle (±30 %)

### R3
- 6 912 XP avant 26, les rendus suffisent → **vrai** (base)
- « 4 quêtes aux Paluns » → **faux** : il y en a 5 (base)
- « 9 autres quêtes […] à Forgefer, Hurlevent, aux Carmines ou au Bois de la Pénombre » → **partiellement faux** : aucune n'est au Bois de la Pénombre ; elles sont en Dun Morogh, à Elwynn, au Loch Modan et dans la Marche de l'Ouest (base)
- Système d'Héritage, « Bien reposé » → le sort **existe** (base, id 429959). « Disponible dès le niveau 25 » et le bénéfice pour le second perso ne sont **pas vérifiés**.
- Donjon « niveau 26–32 » → **faux** : 24-29 (base)
- *Transport de relique perdue* « à rendre au Prospecteur Whelgar » → **introuvable** : le guide donne *Lost Relic Carry* reçue du Gardien des reliques dans le donjon, et le PNJ de rendu n'est pas confirmé (base, method.gg)
- Chaîne de Rethiel « Piétinement, Tabou du feu, Cloques sur la terre » → **faux** : *Piétinements de pattes* et *Feu interdit* sont déjà faites, *Fièvre sur le pays* est en cours (base)
- Prendre *À la recherche de Lame-chantante* et débloquer *Peaux des hautes-terres* → **inadapté** : les deux sont déjà dans le journal (base)
- Monstres de donjon à +50 % d'XP → **vrai** pour le correctif du 9/11, mais l'XP reste inférieure à Classic, ce qui n'est pas dit (connaissances [METHOD-XP])
- Campement : « +5 % d'XP sur les éliminations » → **introuvable** (connaissances du plugin : bonus de métier, tente de repos)
- Quête de classe de chasseur au niveau 30 en capitale → **introuvable**, et douteux
- Gnomeregan et Mirage Raceway → existent, mais Mirage Raceway est trop haut pour 29-30

## Verdict
- **R2 gagne nettement** : chaque quête, PNJ, /way et objet vérifié existe dans la base Forever, et le plan suit le vrai journal (rendus par zone, maître de classe, rang de dépeçage). L'XP est donnée comme une estimation Classic.
- R1 est générique et invente une chaîne aux Paluns (Howin Kindfeather est aux Hinterlands, niveau 45). R3 se trompe sur le niveau du donjon, ignore le journal et affirme des bonus et une quête de classe non vérifiés.
- Ce que R2 a raté : il suggère une quête de niveau 20 hors zone (*Fiora Longears*, vers Theramore) et une quête de niveau 33 (*Syndicat d'assassins*), sans signaler qu'elles sont peu rentables ou risquées. Il ne parle pas non plus des 14 quêtes grises à abandonner nommément, ni des munitions.

{"id":"C14","R1":4,"R2":12,"R3":3}
