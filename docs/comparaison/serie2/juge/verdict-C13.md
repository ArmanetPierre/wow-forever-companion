# Verdict C13 — Plan Ingénierie niveau 45, coût optimisé

| | Faits | Pas de confusion Classic | Plan | Perso | Incertitude | Hallucinations | Total |
|---|---|---|---|---|---|---|---|
| R1 | 1 | 1 | 1 | 0 | 1 | 1 | **5** |
| R2 | 1 | 2 | 2 | 1 | 1 | 1 | **8** |
| R3 | 1 | 2 | 1 | 2 | 2 | 2 | **10** |

Justification des 0 :
- R1, Perso = 0 : « Va à Forgefer et apprends Ingénierie. » Le perso a déjà deux métiers principaux (Travail du cuir 106, Dépeçage 141), donc il ne peut pas apprendre l'ingénierie sans en oublier un. R1 ne le relève pas et ne tient pas compte non plus des 2 po 40. Le plan est générique.

## Faits vérifiés

### R1
- Schéma Rouages en thorium vendu à Forgefer → **vrai** : Gearcutter Cogspinner, Forgefer /way 67.8 42.5 (base, item 16042).
- Schéma Tube en thorium chez Xizzer Fizzbolt, Berceau-de-l'Hiver → **vrai** (base, item 16047, PNJ 11185).
- « Lié quand ramassé » pour ce schéma → **introuvable** (c'est un schéma vendu par un PNJ, l'affirmation est douteuse).
- Micro-ajusteur gyromatique, palier ≈175-195 → **vrai** (base, item 10498, rang estimé 175).
- Mouton explosif ≈160-175, Bidule bourdonnant en bronze ≈125-150 → **vrai** (base, items 4384 et 4375).
- Lunette standard demande de l'Agate mousse → **vrai** (base, item 1206 : « Composant de : Lunette standard »).
- « Clé plate en arclite » → nom **faux** : l'objet s'appelle « Clé plate » (base, item 6219).
- Artisan à Gadgetzan → **vrai** : Buzzek Bracketswing, Tanaris (base, PNJ 8736).
- Rangs à 50, 125 et 200 de compétence, niveaux 10, 20 et 35 → schéma **Classic**. Les guides Forever placent les plafonds à 75, 150, 225 et 300 (wowhead/forever, dving.net). Ce n'est pas faux, mais ce n'est pas vérifié pour Forever.
- « Route vérifiée sur les données de progression Forever du 13 novembre 2026 » → **non vérifiable**, assurance sans fondement.
- Liste d'achats incohérente : 126 barres de bronze au total, mais 50 au palier 2 ; 30 Poudres explosives lourdes « à acheter » alors qu'aucune étape ne les fabrique → erreur interne.
- Placeholder « [perso] » et sources douteuses (« Ethilos ») laissés dans le texte.

### R2
- Reagent Bot à 20, avec Poignée de boulons en cuivre et Tube en cuivre → **vrai** : https://www.icy-veins.com/wow-forever/engineering, https://mobalytics.gg/wow-forever/guides/engineering-profession-guide ; base : le Tube en cuivre est « Composant de : Robot vendeur de composants ».
- Repair Bot à 140, avec 2 Bidules bourdonnants en bronze et 1 Tube en bronze → **vrai en partie** (base, item 279949, rang ≈140 ; Icy Veins). R2 omet le Cuir lourd et surtout le plan, qui tombe sur Sneed aux Mortemines (https://warcraft.wiki.gg/wiki/Blueprint:_Repair_Bot).
- Fritz Fizzle, Les Carmines, schémas payés en Faveur des marchands → **vrai** : https://www.wow-professions.com/forever/npc/fritz-fizzle, https://warcraft.wiki.gg/wiki/Merchant's_Favor.
- Titre « l'Ingénieur » pour 1 000 points de Faveur à 300 → **source unique** (dving.net), non recoupé.
- Kaylaena Springwhisper au Mont Hyjal comme formateur Artisan → **confirmé par des guides Forever** (résultats web, gfinityesports et dving).
- Schéma Rouages en thorium chez Gearcutter Cogspinner, Forgefer → **vrai** (base).
- Balles en mithril à fort impact → **existe** (base : « Balles perçantes en mithril », item 10512).
- Obus en thorium proposés en alternative → schéma **en butin** (base, item 16051 : butin courant, Steppes ardentes), non disponible chez un formateur. R2 ne le signale pas.
- « 15 × Rubis étoilé » dans la liste d'achats, et le Tube en thorium présenté comme lié au prix des Rubis étoilés → **faux / incohérent** : aucune recette du parcours n'utilise le Rubis étoilé (item 7910, base).
- « Cuirasse en bronze (Bronze Framework) » → mauvaise traduction : l'objet s'appelle Structure en bronze (base, item 4382).

### R3
- Le perso a déjà deux métiers principaux et doit en oublier un → **vrai** (base, profil : Travail du cuir 106/150, Dépeçage 141/150).
- Clé plate, 6 barres de cuivre, à 50 → **vrai** pour le nom (base, item 6219, rang ≈50).
- Tube en cuivre, Espingole grossière, Catalyseur léger → **existent** (base : items 4361, 4362, 2880).
- Gyrochronatome, Contrefiche en fer → **existent** (base, items 4389 et 4387 ; Rankedboost cite le Gyrochronatome pour Expert).
- « Gadget en thorium » (Rouage en thorium) pour 250-300 → **vrai** (base, rang ≈260).
- Poudre d'explosion dense à 150-200 et poudre solide à 200-250 → **faux** (paliers ≈250 et ≈175 dans tous les guides). L'erreur est atténuée par la mention « paliers indicatifs, souvenir Classic ».
- Balles en thorium, « au bout du parcours » → le schéma est **en butin** (base, item 16051), ce que R3 ne précise pas.
- Formateurs à 75, 150 et 225 dans les guides Forever → **vrai** (résultats web, wowhead/forever et dving.net).
- Aucun prix de l'HV donné → honnête : R3 propose de calculer le budget à partir des prix relevés par le joueur.

## Verdict
R3 gagne : c'est la seule réponse qui voit le blocage réel (deux métiers principaux déjà pris) et la contrainte d'or (2 po 40), qui refuse d'inventer des prix et qui étiquette son parcours comme souvenir Classic à vérifier.
R2 a le plan le plus actionnable, avec les vrais ajouts Forever (Reagent Bot, Repair Bot, Faveur des marchands), mais il rate le problème des métiers, ne dit rien de l'incertitude et glisse des Rubis étoilés qui ne servent à rien. R1 présente un parcours Classic comme « vérifié Forever » et ignore le perso.
Ce que R3 a raté : un ordre de recettes juste (poudres dense et solide inversées), des quantités par recette et les recettes Forever utiles à monter (Reagent Bot à 20, Repair Bot à 140, schémas en Faveur des marchands).

{"id":"C13","R1":5,"R2":8,"R3":10}
