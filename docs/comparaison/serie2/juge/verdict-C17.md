# Verdict C17

Question : « J'ai deux persos. Comment organiser leurs métiers pour qu'ils se fournissent entre eux, et qui doit faire quoi en premier ? »

## Notes

| Critère | R1 | R2 | R3 |
|---|---|---|---|
| 1. Justesse des faits | 1 | 1 | 1 |
| 2. Pas de confusion Classic | 1 | 1 | 2 |
| 3. Qualité du plan | 1 | 2 | 2 |
| 4. Prise en compte du perso | 1 | 2 | 2 |
| 5. Honnêteté sur l'incertitude | 1 | 1 | 2 |
| 6. Hallucinations | 2 | 1 | 2 |
| **Total /12** | **7** | **8** | **11** |

Aucun 0.

## Contexte vérifié (fc.py)
- `characters comparer` : Brannok (Nain Chasseur 25, 2 po 40) a Travail du cuir 106/150, Dépeçage 141/150 et Cuisine 20/75. Elwyn (Elfe de la nuit Prêtre 11, 16 pa 36) a Herboristerie 3/75 et Cuisine 1/75. Elwyn a donc **un emplacement de métier principal libre** : l'alchimie est un choix logique, et les trois réponses le proposent.
- Base de connaissances (forever-essentiels.md, « probable ») : **dans Forever, les potions de soins sont des recettes de Secourisme**. La base locale le confirme : Potion de soins mineure ≈25 et Potion de soins inférieure ≈65 sont listées en Secourisme. Les plafonds des rangs de formateur sont les mêmes que dans Classic.

## Faits vérifiés

### R1
- Le chasseur porte de la maille à partir du niveau 40 → vrai (règle générale, inchangée).
- Elwyn a Herboristerie et un 2e métier à choisir → vrai (base perso).
- L'alchimie produit des potions de soin pour les deux persos → **faux dans Forever** : les potions de soins relèvent du Secourisme (base locale et connaissance). C'est une confusion Classic, mais l'alchimie reste utile pour les élixirs et le mana, donc le plan tient.
- 13 quêtes terminées → vrai (`quests a_rendre`). « 4 quêtes aux Paluns » → à peu près vrai : 4 rattachées aux Paluns, plus 1 à Excavations : les Paluns.
- Option B « Couture + Enchanteur (ou Herboristerie) » → vague, et elle n'apporte rien à l'échange entre les deux persos.
- Pas de mention du plafond 150 ni du rang Expert, alors que Brannok est à 141/150 en dépeçage. Pas de mention du secourisme.

### R2
- Dépeçage 141, Cuir 106, Cuisine 20, Elwyn niveau 11 → vrai (base perso).
- « Potions de soin pour [perso] » fabriquées par l'alchimie → **faux dans Forever** (Secourisme) : confusion Classic.
- Les métiers secondaires ne prennent pas d'emplacement principal → vrai (2 principaux, 3 secondaires : connaissance [BLZ-GUIDE]).
- Le campement (« Camping ») présenté comme un métier secondaire → faux : c'est un système de feux de camp, pas un métier (connaissance « Métiers »).
- Travail du cuir 20 → tente (bonus de repos) → vrai. Dépeçage 20 → chaise de camp (+critique) → vrai (connaissance, probable).
- Herboristerie 20 → Bougie d'encens → vrai (recette ≈20 : Pacifique + Feuillargent). « Bonus d'Intelligence » → introuvable : la fiche de l'objet 279962 n'affiche aucune stat, et l'affirmation est donnée comme sûre.
- « Faire monter Travail du cuir vers 150 » → incomplet : rien n'est dit sur la formation Expert nécessaire pour dépasser 150.
- Le nom « Premiers soins » au lieu de « Secourisme » (nom FR du client) → mineur.

### R3
- Cuir 106/150, Dépeçage 141/150, Herboristerie 3/75, Elwyn 16 pa → vrai (base perso).
- « Dans Forever, les potions de soins sont des recettes de secourisme » → vrai (base locale et connaissance, probable).
- Gants d'agilité en cuir ≈120, +4 Agi +4 End, 1 Élixir d'Agilité mineure → vrai (`professions` Brannok).
- Bottes de défenseur en cuir ≈110, 3 Élixirs de Robustesse mineure → vrai (`professions` Brannok).
- Pacifique + Feuillargent → Élixir de défense mineure (Feuillargent + Pacifique), Élixir de Force mineure (variante Feuillargent seul), Puits de mana (Pacifique) → vrai (`professions` Alchimie).
- Alchimie à Darnassus, Terrasse des artisans → vrai (Ainethil, Alchimiste, Darnassus /way 54.9 24.0).
- Formateurs Expert à Forgefer, niveau 20 requis → vrai : Fimble Finespindle <Artisan du cuir - Expert> et Ecorchepierre Balthus sont à Forgefer.
- « Passe-le en Expert tout de suite » → **partiellement faux** : le rang Expert de travail du cuir demande **125** de compétence et Brannok est à 106. C'est possible tout de suite pour le dépeçage (141), pas pour le cuir. Sources : https://www.icy-veins.com/wow-forever/leatherworking-leveling-guide et https://www.wow-professions.com/forever/leatherworking-leveling-guide
- Poste de travail du cuir à 125 → vrai (connaissance, probable).
- Objet de campement à 20 de compétence → vrai (connaissance).
- Les rangs sont signalés comme estimés (≈) et la source des recettes comme inconnue → honnête.

## Verdict
R3 gagne nettement (11). C'est la seule réponse qui évite le piège Classic des potions de soins, qui relie concrètement les deux persos par des recettes vérifiées, et qui tient compte de l'or réel de chaque perso (16 pa contre 2 po 40).
R2 (8) est complet et bien ordonné. R1 (7) est plus vague. Tous deux font reposer l'intérêt de l'alchimie sur des potions de soins, qui relèvent du secourisme dans Forever.
Ce que R3 a raté : le travail du cuir ne peut pas passer Expert « tout de suite », car il faut 125 de compétence (Brannok est à 106). Seul le dépeçage le peut maintenant. Il fallait dire de monter le cuir à 125 d'abord.

{"id":"C17","R1":7,"R2":8,"R3":11}
