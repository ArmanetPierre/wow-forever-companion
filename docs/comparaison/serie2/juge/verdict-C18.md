# Verdict C18 — talents, rotation et équipement avant les donjons (chasseur)

## Notes

| Critère | R1 | R2 | R3 |
|---|---|---|---|
| 1. Justesse des faits | 2 | 0 | 2 |
| 2. Pas de confusion Classic | 2 | 1 | 2 |
| 3. Qualité du plan | 2 | 1 | 1 |
| 4. Prise en compte du perso | 2 | 1 | 1 |
| 5. Honnêteté sur l'incertitude | 2 | 0 | 2 |
| 6. Hallucinations | 2 | 0 | 2 |
| **Total /12** | **12** | **3** | **10** |

Justification des 0 :
- R2, critère 1 : « Gnomeregan » proposé au niveau 25 alors que la base le donne pour les niveaux 29-38 ; « utilise Feu feint pour lâcher l'aggro » alors que Feindre la mort s'apprend au niveau 30.
- R2, critère 5 : « cela te fera passer niveau 26 instantanément », affirmé sans calcul.
- R2, critère 6 : talents inventés (« Endurance de la nature (5/5) », « Peau de serpent renforcée », « Ordre de tuer / Réflexes félins ») et « Tir assuré », un sort qui n'existe ni dans Classic ni dans Forever. Ces inventions changent le conseil sur les talents et la rotation.

R2 et R3 ne connaissent pas les talents réels. R3 le dit lui-même : « je n'ai pas encore ton arbre de talents ». Leur note pour la prise en compte du perso est donc plafonnée à 1.

## Faits vérifiés

Données réelles : `fc.py talents` donne Aspects mortels 3/5, Œil de faucon 3/3, Trait de choc amélioré 1/5, Attaques mortelles 4/5, Morsures et piqûres améliorées 1/3, Visée minutieuse 2/5, Tir des arcanes amélioré 2/5, soit 16/16 points. `fc.py gear` donne : cou et tête vides, Bouquet d'Auberdine dans les sacs, réparation 29 pc.

### R1
- Les 7 talents et leurs rangs, 16/16 points → **vrai** (fc.py talents).
- Excavations : les Paluns, niveaux 24-29 → **vrai** (base, dungeon).
- Boss Seléchine, Dent-Sombre, Horreur des hautes-terres, Gardien des reliques → **vrai** (base, dungeon).
- Butin des boss non répertorié → **vrai** (la base dit « pas dans les fichiers du client »).
- Bouquet de fleurs d'Auberdine (+4 End) dans les sacs, réparation 29 pc → **vrai** (fc.py gear).
- Jambières pétrolifères (+14 Agi, +6 End, environ +2 DPS), Gants griffe-de-loup, Mantelet des voleurs (+0,7 DPS) → **vrai** (fc.py gear).
- Médaillon de Sentinelle vendu par Illiyana Moonblaze → **vrai** (base). La condition de réputation est signalée comme venant de Classic.
- Casque de bagarreur en cuir (+10 Agi, +13 End), Travail du cuir ≈150 contre 106 → **vrai** (base, item 252512).
- Carabine de Dun Garok de source inconnue → **vrai** (base : « source non répertoriée »).
- Tir rapide au niveau 26, Feindre la mort au niveau 30 → **vrai** (https://warcraft.wiki.gg/wiki/Hunter_abilities_(Forever)).
- Visée en 2 s d'incantation, temps de recharge partagé avec Flèches multiples → **vrai** dans Forever (https://www.method.gg/wow-forever/wow-forever-hunter-leveling-guide-and-talents).
- Quête « À la recherche de Lame-chantante » à rendre et liée au donjon, « Cuir des hautes-terres » → **vrai** (base, dungeon : journal du donjon).
- Mortemines 17-26, quête « La Confrérie défias » → **vrai** (base).
- Méthode conseillant Maîtrise des bêtes et Invocation de faucon au niveau 25 → **vrai** (Method).
- Première respé à environ 1 po → **non vérifié** (valeur de Classic, présentée avec prudence).

### R2
- Gnomeregan adapté au niveau 25 → **faux** (base : niveaux 29-38).
- « Feu feint » (Feindre la mort) disponible → **faux** au niveau 25 (niveau 30, warcraft.wiki.gg).
- « Tir assuré » → **faux** : le sort est absent de Forever (ni la page des capacités ni Method ne le mentionnent).
- Talents « Endurance de la nature », « Peau de serpent renforcée », « Ordre de tuer », « Réflexes félins » → **introuvables ou faux** : absents de la base, de warcraft.wiki.gg et de Method.
- Félin heureux = 125 % de dégâts → règle de **Classic** présentée sans badge.
- 13 quêtes à rendre, 6 912 XP, fusil à 13,3 DPS → **vrai**, mais repris du contexte fourni.
- « Dépeçage… pour monter ton métier (actuellement 141) » → confusion : 141 est le niveau de Dépeçage, pas de Travail du cuir.
- Ne connaît pas les talents actuels → **vrai** : il ne les cite pas.

### R3
- 16 points de talents au niveau 25 → **vrai**.
- Invocation de faucon : talent de Maîtrise des bêtes au palier 25, 2 faucons au plus, 18 s, temps de recharge partagé avec Tir des arcanes → **vrai** (Method, base de connaissances du plugin).
- Tir concentré (Focused Fire) 2/2 → **vrai**, le talent existe dans Forever (warcraft.wiki.gg).
- Entraînement à l'endurance, Fureur déchaînée, Aspects mortels → **vrai** (Method).
- Mobalytics recommande Maîtrise des bêtes → **vrai**, d'après la base de connaissances du plugin.
- Désactiver Grondement, Marque du chasseur, Aspect du faucon, Piège givrant → **vrai** et adapté.
- « Jambières de trappeur » et « capuchon de bagarreur » selon ForeverDB → **introuvables** dans la base. Le casque connu s'appelle « Casque de bagarreur en cuir ». Erreur mineure, la source est citée.
- Talents actuels → **inconnus**, et R3 l'avoue. Il conseille Maîtrise des bêtes sans voir que le perso est en Précision, sans parler de respé ni de son coût.
- Équipement : seulement des catégories (casque, jambières…), aucun objet, aucun donjon nommé.

## Verdict
R1 gagne nettement. Il part des talents et de l'équipement réels et nomme le bon donjon (Excavations : les Paluns, 24-29) et ses boss. Il donne des améliorations chiffrées et une rotation conforme à Forever (Visée en 2 s, recharge partagée avec Flèches multiples, Tir rapide au niveau 26).
R3 est honnête et juste, mais générique : il ne connaît ni les talents ni l'équipement. R2 invente des talents et des sorts (Tir assuré, Ordre de tuer, Feindre la mort avant 30) et envoie le joueur à Gnomeregan.
Ce que R1 a raté : il ne propose pas d'objet concret que le joueur peut obtenir rapidement pour le cou. Le Médaillon de Sentinelle demande probablement une réputation au Goulet, et la Rune de perfection, plus accessible, n'est pas citée. Il n'évoque pas non plus la Main gauche ni le niveau du félin pour le groupe.

{"id":"C18","R1":12,"R2":3,"R3":10}
