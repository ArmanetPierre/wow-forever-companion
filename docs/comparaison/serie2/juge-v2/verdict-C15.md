# Verdict C15 : Excavations : les Paluns (stratégie, boss, pièges, quêtes, loot chasseur)

## Notes

| Critère | R1 | R2 | R3 |
|---|---|---|---|
| 1. Justesse des faits | 0 | 1 | 1 |
| 2. Pas de confusion Classic | 0 | 2 | 2 |
| 3. Qualité du plan | 0 | 1 | 2 |
| 4. Prise en compte du perso | 1 | 1 | 2 |
| 5. Honnêteté sur l'incertitude | 0 | 1 | 2 |
| 6. Hallucinations | 0 | 1 | 2 |
| **Total /12** | **1** | **7** | **11** |

Justification des 0 :
- R1, critère 1 : « ne sont pas une instance/donjon instancié, mais une zone élite extérieure ». Faux : la base locale liste un donjon Forever « Excavations : les Paluns », niveaux 24-29, carte 2998, avec 4 boss.
- R1, critère 2 : tout le plan décrit le site de Whelgar de Classic (zone extérieure, Sarltooth, Ormer, Prospecteur Whelgar) au lieu du donjon Forever.
- R1, critère 3 : le plan mène à une zone extérieure et ne parle d'aucun des boss réels. Il est inutilisable pour la question posée.
- R1, critère 5 : affirme sans réserve « Il n'y a pas de boss de donjon ».
- R1, critère 6 : « Bague de reconnaissance de Whelgar », un butin de quête inventé (introuvable), et « Piège explosif » débloqué au niveau 26 (niveau 34 dans Classic).

## Faits vérifiés

### R1
- Excavations = zone extérieure, pas une instance → **faux** (base, `dungeon` : donjon Forever, 24-29, 4 boss ; method.gg).
- Boss « Sarltooth / Dent-de-sarl » niv. 28-29 → **faux pour ce donjon** : Grondecroc (PNJ 1353, niv. 29) est un mob nommé extérieur de Classic aux Paluns (`/way 33.3 51.5`) et ne fait pas partie des boss du donjon (base).
- Ormer Tresse-de-fer et Prospecteur Whelgar comme donneurs → les PNJ existent (1078, 1077), mais ils donnent les quêtes Classic et pas celles du donjon (base, method.gg).
- « Bague de reconnaissance de Whelgar » → **introuvable** (base), probablement inventée.
- Patrons verts « Gants en cuir de raptor » qui tombent des mobs → **non vérifié et hors sujet**.
- Marque du chasseur rang 2 et Piège explosif au niveau 26 → **faux** (le Piège explosif s'apprend au niveau 34 dans Classic).
- Aucun des boss réels (Seléchine, Dent-Sombre, Horreur des hautes-terres, Gardien des reliques) n'est cité, et le fusil n'est pas mentionné → **omission majeure**.

### R2
- 4 secteurs et 4 boss : Seléchine, Dent-Sombre, Horreur des hautes-terres, Gardien des reliques → **vrai** (base).
- Le Gardien est activé par un panneau de contrôle et passe niveau 31 → **vrai** (base, method.gg).
- Golemsight Long Gun : 29-54, vitesse 2,5, 16,6 DPS, +6 Agi → **vrai** (base, id 273029).
- Dent-Sombre enrage à 30 % → **faux** : c'est à 20 % (base, method.gg).
- Tempête de poussière de Seléchine « réduit leur précision » → **faux** : elle réduit la menace du tank (base, method.gg).
- Reliquary Mantle « 12 End, 4 Esprit » → **faux** : 12 End, +4 Toucher (base, id 273028).
- Ring of Power Regulation « 8 End, 2 mana/5 s » → **faux** : +6 puissance des sorts (base, id 273030).
- Cape anti-poussière « 4 For, 4 Agi, 7 Int » → l'objet existe mais les stats sont **fausses** : 5 Agi, 5 Int, 5 Esp (base, id 271716). Sa source (chaîne de la Relique) n'est pas confirmée.
- « Les Matriarches appellent des renforts » → **faux ou inventé** : selon method.gg, elles lancent Pourfendre la chair (saignement).
- « Araignées : maladie » → **faux** : les araignées empoisonnent, la maladie vient des Chasseurs des fourrés (method.gg).
- Cuir des hautes-terres : James Halloran, 4 peaux de raptor des fourrés → **vrai** (base, quête 98815).
- Dorin Songblade aux Carmines et Caitlin Grassman à Menethil → **vrai** (method.gg).
- Quêtes « Chute dans les marais », « Cœur tressé », « La relique égarée » → **introuvables** (base et method.gg).
- « tu as la quête Alliance » (Horreurs dans les hautes-terres) → **faux** : elle n'est pas dans le journal, et la réponse ne dit pas qu'elle exige la chaîne du Gardien vert.
- Le loot cuir du chasseur, Atours de plumes bigarrées (Dent-Sombre), est **omis**.

### R3
- Fourchette 24-29, groupe de 5 → **vrai** (base).
- Entrée près de Dun Algaz, au pied de la montagne → **vrai** (method.gg).
- Cuir des hautes-terres : 4 peaux de raptor des fourrés, déjà dans le journal → **vrai** (base, données perso).
- Horrors in the Highland exige la chaîne du Gardien vert → **vrai** (method.gg, base).
- « Rends d'abord À la recherche de Lame-chantante (Dorin Songblade, Les Carmines /way 25.8 46.4) » → **imprécis** : la quête est bien à rendre, mais le point de rendu en jeu est aux Paluns `/way 48.2 56.5`. Les coordonnées données sont celles du donneur (base, quête 95772).
- Tempête de poussière : fait tomber la menace du tank → **vrai** (base).
- Dent-Sombre : Rugissement terrifiant vers les packs cachés, enrage à 20 % → **vrai** (base, method.gg).
- L'Horreur ne lâche que l'objet de quête → **vrai** (base).
- Gardien : Panneau de contrôle titan, niveau 31, Choc martial, Frappe en arc, Relique titan sur le corps → **vrai** (base).
- Arme d'épaule mire-de-golem : 16,6 DPS, +6 Agi, niv. 28, +3,8 DPS → **vrai** (base).
- Atours de plumes bigarrées : +9 Agi, +15 Int, +1,3 DPS, +29 armure face à la Tunique de barde du sanglier équipée → **vrai** (base, `gear`).
- Jambières en peau de panse souple : +7 End seulement → **vrai** (base).
- Chasseurs des fourrés et araignées : blessure infectée et poison à dissiper → **vrai** (method.gg).

## Verdict
- **R3 gagne** (11/12). Ses affirmations sont exactes et sourcées (base locale + method.gg), il répond à tous les volets de la question, il s'appuie sur le journal, le fusil et le torse portés, et il sépare le sûr du probable.
- R2 (7/12) a la bonne structure et le bon fusil, mais de nombreux détails sont faux : enrage, Tempête de poussière, stats des objets, Matriarches. Il oublie aussi le torse cuir. R1 (1/12) confond le donjon Forever avec la zone Classic du site de Whelgar.
- Ce que R3 a raté : le point de rendu de « À la recherche de Lame-chantante » (aux Paluns `/way 48.2 56.5`, pas chez Dorin aux Carmines), la quête *Lost Relic Carry* donnée dans le donjon, et l'idée de passer 26 avant d'entrer.

{"id":"C15","R1":1,"R2":7,"R3":11}
