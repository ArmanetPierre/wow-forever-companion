# Verdict C17 — « Deux persos : organiser les métiers pour qu'ils se fournissent, qui fait quoi en premier ? »

## Notes

| Critère | R1 | R2 | R3 |
|---|---|---|---|
| 1. Justesse des faits | 1 | 1 | 1 |
| 2. Pas de confusion Classic | 2 | 0 | 0 |
| 3. Qualité du plan | 2 | 1 | 1 |
| 4. Prise en compte du perso | 2 | 1 | 1 |
| 5. Honnêteté sur l'incertitude | 2 | 1 | 0 |
| 6. Hallucinations | 2 | 2 | 2 |
| **Total /12** | **11** | **6** | **5** |

Justification des 0 :
- R2, critère 2 : « L'Alchimie devient complémentaire au Chasseur, notamment pour les potions de soin » : dans Forever, les six potions de soins sont des recettes de Secourisme. Le choix de l'Alchimie pour le prêtre repose sur cette règle Classic.
- R3, critère 2 : « L'Alchimie produit des potions de soin, de mana… Pourquoi c'est vital » : même erreur, et c'est l'option « recommandée ».
- R3, critère 5 : aucune nuance nulle part, « la règle d'or est… », règle Classic assénée comme sûre.

## Faits vérifiés

### R1
- Fimble Finespindle, Artisan du cuir Expert, Forgefer `/way 40.2 33.7` → **vrai** (base, PNJ 5127)
- Trianna, couture, Darnassus `/way 63.5 21.2` → **vrai** (base, PNJ 11050, Tailleur Compagnon)
- Dannelor, secourisme, Darnassus `/way 51.7 12.2` → **vrai** (base, PNJ 4211)
- Thamner Pol, secourisme, Dun Morogh `/way 47.2 52.6` → **vrai** (base, PNJ 2326 « Médecin »)
- « Dans Forever, les potions de soins se font avec le Secourisme (une herbe, une fiole et des épices) » → **vrai** (base, connaissance « Secourisme Forever », recettes 1244431-1244436)
- Gilet rouge en lin +2 Int, +1 puissance des sorts → **vrai** (base, item 6239, modifié par Forever)
- Sac en laine ≈75 → **vrai** (rang estimé, base item 4240) ; Sac en lin ≈25 non vérifié précisément, rang présenté comme estimé
- Cuir moyen = 4 Cuir léger, ~14 fabrications, 11 cuirs légers en sacs → **vrai** (base, parcours de métier : 56 cuirs légers pour 14)
- Expert à 125 en Travail du cuir → **vrai pour la base** (seuil Classic, signalé « à vérifier »)
- Tente du camp dans les sacs, 8 places libres, sacs de 6 à 10 places → **vrai** (données Brannok)
- 10 Etoffe de lin + 10 Etoffe de laine sur le chasseur → **vrai** (sacs Brannok)
- « Les 29 Etoffe de lin de ses sacs » (prêtre) → **faux mineur** : elles sont en banque, pas en sacs (données Elwyn)
- Brannok n'a pas le Secourisme → **vrai** (métiers capturés)
- Avertissement « deux royaumes différents, pas de courrier » → **douteux** : Forever a un méga-royaume par ruleset et région (base, connaissance « Rulesets ») ; les deux persos sont EU JcJ. R1 le signale bien comme « souvenir Classic, à vérifier », mais l'avertissement est probablement sans objet.

### R2
- Travail du cuir 20 → Tente du camp, repos → **vrai** (base, connaissance « Campement »)
- Dépeçage 20 → Chaise du camp, bonus de critique → **vrai** (base, +2 % crit au 60)
- Herboristerie 20 → Bougie d'encens → **vrai** (base ; bonus d'Intelligence non vérifié)
- Alchimie pour les potions de soin → **faux dans Forever** (Secourisme ; base, connaissance « Secourisme Forever »)
- Alchimie pour potions de mana et élixirs → **vrai** (base : Élixir d'Esprit mineur, Puits de mana, etc.)
- « Rendre les 4 quêtes terminées aux Paluns » → **globalement vrai** (4 quêtes de la catégorie Paluns, plus 1 « Excavations » rendue aux Paluns ; base, journal Brannok)
- Métiers secondaires sans slot principal → **vrai** (général)
- « Camping » présenté comme un métier secondaire → **imprécis** : le campement est un système lié aux métiers, pas un métier
- Ne mentionne ni formateur ni lieu ni quantité : rien à vérifier de ce côté

### R3
- Le chasseur porte la maille à partir du niveau 40 → **vrai en Classic**, non contredit dans la base, non signalé
- Le Travail du cuir produit du cuir, de la maille et des kits d'armure → **vrai**
- Alchimie pour les potions de soin → **faux dans Forever** (base, Secourisme)
- « 4 quêtes situées aux Paluns » à rendre → **globalement vrai** (journal Brannok)
- Herboristerie 3, Cuisine 1 pour le prêtre → **vrai** (données Elwyn)
- Option B « Couture + Enchanteur (ou Herboristerie) » → incohérent (ne crée aucun lien entre les deux persos), pas faux en soi
- Aucun nom de PNJ, d'objet ou de recette à vérifier

## Verdict
1. **R1 gagne nettement (11/12)** : c'est la seule réponse qui connaît la règle propre à Forever (potions de soins par le Secourisme). Elle construit une vraie boucle herbes → Secourisme pour les deux, tissu → Couture → sacs, et donne formateurs, /way, quantités et stocks réels.
2. R2 (6) et R3 (5) recommandent l'Alchimie pour les potions de soin, une règle Classic fausse dans Forever. R2 se rattrape un peu avec les objets de campement exacts et un bon « rends d'abord tes quêtes ». R3 est générique et sans aucune nuance.
3. Ce que R1 a raté : l'avertissement sur les royaumes est probablement sans objet (méga-royaume par ruleset). Il place le lin du prêtre « dans ses sacs » alors qu'il est en banque. Il ne dit pas de rendre d'abord les 13 quêtes du journal plein, ni que le chasseur a déjà 22 Cuirs moyens.
