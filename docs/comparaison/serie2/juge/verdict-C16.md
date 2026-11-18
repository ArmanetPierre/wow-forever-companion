# Verdict C16 — « Avec mes métiers, quelle est la meilleure façon de me faire de l'or à mon niveau ? »

## Notes

| Critère | R1 | R2 | R3 |
|---|---|---|---|
| 1. Justesse des faits | 1 | 0 | 1 |
| 2. Pas de confusion Classic | 1 | 1 | 2 |
| 3. Qualité du plan | 1 | 1 | 2 |
| 4. Prise en compte du perso | 1 | 1 | 2 |
| 5. Honnêteté sur l'incertitude | 1 | 0 | 2 |
| 6. Hallucinations | 1 | 0 | 2 |
| **Total /12** | **6** | **3** | **11** |

Justification des 0 :
- R2, critère 1 : « Passer niveau 26 va vous débloquer […] de meilleures recettes de Travail du cuir et surtout […] du Cuir lourd ». Les recettes et le cuir récolté dépendent du rang de métier et du niveau des bêtes, pas du niveau du perso. Et le vrai blocage, le plafond 150 du Dépeçage, n'est pas mentionné.
- R2, critère 5 : « Ne vendez jamais vos cuirs au marchand », « très recherchés à l'HdV ». Ce sont des affirmations de marché sans aucune réserve, alors que personne n'a les prix de l'HV de Forever.
- R2, critère 6 : « Paniers de cuir léger » est introuvable dans la base, donc probablement inventé. La réponse renvoie aussi à « Cette vidéo détaille… » sans qu'aucune vidéo n'existe.

## Faits vérifiés

### R1
- Dépeçage 141, Travail du cuir 106, Cuisine 20 → **vrai** (fc.py professions).
- Le Dépeçage donne du Cuir léger et du Cuir moyen → **vrai** (sacs : Cuir léger ×11, Cuir moyen ×22).
- Le « Pristine Leather » est un matériau rare de Dépeçage propre à Forever, utilisé dans de nombreuses recettes → **vrai**. C'est le Cuir immaculé (id 249427, composant de recettes de forge et de bottes de Travail du cuir), ce que confirment la base et https://www.icy-veins.com/wow-forever/news/every-gathering-node-in-wow-forever-can-drop-a-scarce-material-youll-want/ et https://expcarry.com/pristine-leather-farming-wow-forever.
- Le Pristine Leather vient de « bêtes de niveau 10 à 26 » → **plausible / non vérifié** (les guides bêta citent des mobs de bas niveau, item level 25).
- Il vaut « plusieurs fois » le cuir normal → **non vérifiable** (aucun prix HV).
- « Les données de marché récentes montrent que beaucoup de fabrications coûtent davantage… » → **non vérifiable**. L'affirmation est présentée comme sourcée, avec des restes de citations (« Epiccarry +1 », « MMODude », « Wowhead »).
- « 100 po avant le niveau 40 » pour la monture → **non vérifié pour Forever** (c'est la règle Classic).
- R1 ignore que le joueur a déjà 5 Cuirs immaculés et ignore le plafond 150 du Dépeçage → **omission**.
- La formule de profit est illisible (LaTeX cassé).

### R2
- Dépeçage 141 et Travail du cuir 106, Cuir léger et Cuir moyen → **vrai** (base).
- 6 912 XP avant 26 et 13 quêtes à rendre → **vrai** (contexte).
- Crocilisques et raptors aux Paluns → **vrai** (Larme de crocilisque dans les sacs, zone 20-30).
- Le chasseur porte la maille au niveau 40 → **vrai** (note de la base, règle Classic confirmée comme valable).
- « Maudite cotte de mailles » → formulation absurde.
- « Paniers de cuir léger » → **introuvable** (base), probablement inventé.
- Le niveau 26 débloquerait de meilleures recettes et le Cuir lourd → **faux** (cela dépend du rang de métier et du niveau des mobs).
- Le prêtre serait « à Darnassus » → **non vérifié**.
- « Cette vidéo détaille… » → **inventé** (aucune vidéo).
- Le plafond 150 et le formateur ne sont pas mentionnés → **omission majeure**.

### R3
- 2 po 40 pa, 8 places libres, Dépeçage 141/150, Travail du cuir 106/150, Cuisine 20/75 → **vrai** (fc.py bags et professions).
- 22 Cuirs moyens, 11 Cuirs légers, 2 Peaux légères, 5 Cuirs immaculés → **vrai** (fc.py bags).
- Les bottes et capes vers 110-120 demandent du fil, des teintures et des composants rares → **vrai** : Bobine de fil raffiné, Teinture grise, Oeil ténébreux, Peau légère traitée ×4 alors que le joueur n'en a qu'une (base).
- Casque de bagarreur en cuir : rare, niveau 25, +10 Agi, +13 End, 84 d'armure, fabriqué par Travail du cuir à ≈150 → **vrai** (item 252512, rang estimé). Emplacement de tête vide → **vrai** (« emplacement vide : à équiper »).
- Formateur de Dépeçage à Forgefer → **vrai** (Ecorchepierre Balthus, PNJ 6291, /way 39.9 32.5). « Quartier des Artisans » → **non confirmé**.
- Expert monte le plafond à 225 → règle Classic, **signalée** « à vérifier en jeu ».
- « Sinon, tes 9 derniers points sont perdus » → **inexact** : les 9 points sont encore à prendre, c'est seulement la suite qui sera bloquée.
- Arbalète de poing dissimulée à vendre → **discutable** : 15,2 DPS, niveau requis 26, contre 13,3 DPS pour le fusil actuel. C'est une amélioration probable à 26, à condition d'apprendre la compétence Arbalète.
- La réponse ne mentionne pas le Chaperon de bagarreur en cuir (≈125, niveau 20), qui serait plus proche, ni le fait que le patron du casque est rare et de source inconnue → **omission**.
- Acheter de l'or peut mener au bannissement → **plausible** (avertissement général).

## Verdict
R3 gagne nettement. Il s'appuie sur les vrais sacs et métiers (cuirs comptés, plafond 150 à débloquer, casque craftable pour une tête vide), sépare clairement ce qu'il sait de ce qu'il ignore (prix de l'HV) et signale que ses rangs viennent de Classic.
R1 est prudent mais générique. Il colle des pseudo-citations de marché et rate le plafond 150. R2 invente un objet et une vidéo, et se trompe sur ce que débloque le niveau 26.
Ce que R3 a raté : il présente les 9 derniers points comme « perdus », il propose de vendre une arbalète qui sera une amélioration au niveau 26, et il ne dit pas qu'il faut d'abord trouver le patron (rare) du casque ni que le Chaperon (≈125) est plus accessible.
