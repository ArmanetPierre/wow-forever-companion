# Verdict C16 : « Avec mes métiers, quelle est la meilleure façon de me faire de l'or à mon niveau ? »

## Notes

| | Faits | Pas de confusion Classic | Plan | Perso | Incertitude | Hallucinations | Total |
|---|---|---|---|---|---|---|---|
| R1 | 2 | 2 | 1 | 2 | 2 | 2 | **11** |
| R2 | 1 | 2 | 1 | 1 | 1 | 2 | **8** |
| R3 | 1 | 1 | 1 | 1 | 0 | 0 | **4** |

Justification des 0 :
- R3 Incertitude 0 : prix et demande présentés comme certains, sans aucune donnée : « Les pièces offrant des bonus d'agilité ou d'endurance se vendent particulièrement bien ».
- R3 Hallucinations 0 : recette inventée, proposée comme action : « transformez-le en Paniers de cuir léger » (aucun objet de ce type dans la base Forever).

Notes sous 2, R1 Plan 1 : rien sur la Cuisine ni sur le second perso (Herboristerie), alors que la question porte sur « mes métiers ». Aucune zone ni mob précis pour le dépeçage. Le patron du Chaperon est un objet rare : R1 ne dit pas comment l'obtenir.

## Faits vérifiés

### R1
- Dépeçage 141/150, palier Expert accessible (compétence et niveau OK) → **vrai** (base, professions Brannok ; paliers [Classic] signalés par la base)
- Ecorchepierre Balthus, Forgefer, /way 39.9 32.5 → **vrai** (base)
- Règle « compétence = niveau du mob × 5 » → **Classic**, mais R1 la donne explicitement « Sur Classic » → correct
- Cuir immaculé ×5 en sac, revente marchand 1 pa 25, composant de Bottes de vétéran / Ceinture de garde en anneaux (forge) → **vrai** (base, item 249427 ; sacs)
- Cuir moyen ×22, revente marchand 50 pc ; Peau moyenne traitée ×4, revente 2 pa → **vrai** (base, sacs + parcours métier)
- Chaperon de bagarreur en cuir : rang ≈100, +8 Agi, +10 End, 76 armure, tête vide, +1,1 DPS → **vrai** (base, item 252504). Le patron est rare : son mode d'obtention n'est pas vérifié.
- Fimble Finespindle, Forgefer, /way 40.2 33.7, Expert à 125 → **vrai** (base)
- Parcours Cuir moyen puis Peau moyenne traitée, Sel à 50 pc chez Kersok Prond, /way 10.4 60.6, ≈30 pa jusqu'à 150 → **vrai** (base, 30 pa 50 pc)
- Correctif du 10/11 qui baisse le rachat des armures en cuir fabriquées → **vrai** (connaissance Forever [HOTFIX])
- Caisses détournées, Faveur marchande, Marcy Fournier aux Trois chemins des Carmines (≈10 73), un seul objet par caisse, butin aussi en donjon → **vrai** (base PNJ 256390 /way 9.4 71.0 ; note Faveur des marchands)
- Prix des HV et des formations déclarés inconnus → honnête

### R2
- Dépeçage 141, Travail du cuir 106, Cuisine 20, Prêtre 11 Herboristerie 3 → **vrai** (contexte)
- « Pristine Leather » obtenu au dépeçage, bêtes de niveau 10 à 26, utilisé dans des recettes → **plausible** : le cuir existe dans Forever, mais les niveaux viennent de la bêta et les sources se contredisent (https://expcarry.com/pristine-leather-farming-wow-forever, https://www.warcrafttavern.com/forever/guides/skinning/). R2 ne voit pas que le joueur en a déjà 5 en sac (Cuir immaculé).
- Valeur « plusieurs fois supérieure » au cuir normal → **introuvable** (prix d'HV inconnus), mais nuancé
- Herboristerie « l'un des métiers les plus intéressants de l'économie Forever, marchés EU » → **introuvable**, la source citée est un site de boosting
- 100 po avant le niveau 40 pour la monture → **cohérent** (connaissance Forever : 100 po au niveau 40, chiffres de bêta)
- Cuir lourd « très élevée si tu peux en farmer » → peu réaliste au niveau 25, mais conditionnel
- Ne signale pas le blocage du Dépeçage à 150 (Expert à prendre) → **omission importante**
- Formule de profit mal rendue (LaTeX cassé), citations parasites (« Epiccarry +1 ») → forme

### R3
- Les Paluns : crocodiles et raptors de niveau 20-30 → **vrai pour l'essentiel** (crocilisques et raptors ; quêtes de niveau 20-34, base)
- « murlocs (parfois) » cités parmi les bêtes à dépecer → **faux** (les murlocs ne se dépècent pas)
- « Paniers de cuir léger » → **introuvable / inventé** (base : aucun objet de ce nom)
- Chasseurs en maille à partir du niveau 40 → règle **Classic** non signalée
- Passer niveau 26 débloque « de meilleures recettes de Travail du cuir » → **faux** : les recettes dépendent de la compétence et du palier, pas du niveau
- 13 quêtes à rendre, 6 912 XP avant 26 → **vrai** (contexte)
- Le Prêtre « à Darnassus » → **introuvable** dans le contexte
- Ne signale pas le blocage du Dépeçage à 150 ni le palier Expert du Travail du cuir à 125 → omission
- Renvoie à « cette vidéo » qui n'est pas fournie → référence vide

## Verdict
R1 gagne nettement (11/12) : chaque fait concret est vérifié dans la base (PNJ, /way, prix marchands, Cuir immaculé, Chaperon, correctif du 10/11, Faveur marchande), et R1 sépare clairement le sûr de l'inconnu (prix d'HV, coût des formations).
C'est aussi la seule réponse qui voit le vrai blocage (Dépeçage à 141/150 : il faut prendre Expert) et qui s'appuie sur les sacs du joueur. R2 est honnête mais générique. R3 invente une recette et se trompe de mécanique (murlocs, recettes liées au niveau).
Ce que R1 a raté : le second perso (Herboristerie) et la Cuisine, une zone ou un circuit de dépeçage précis, la façon d'obtenir le patron rare du Chaperon, et des « [source] » laissés vides.

{"id":"C16","R1":11,"R2":8,"R3":4}
