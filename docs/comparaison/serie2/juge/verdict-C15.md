# Verdict C15 — Excavations : les Paluns (stratégie, boss, pièges, quêtes, loot chasseur)

| Critère | R1 | R2 | R3 |
|---|---|---|---|
| 1. Justesse des faits | 1 | 2 | 0 |
| 2. Pas de confusion Classic | 2 | 2 | 0 |
| 3. Qualité du plan | 2 | 2 | 0 |
| 4. Prise en compte du perso | 1 | 2 | 1 |
| 5. Honnêteté sur l'incertitude | 1 | 2 | 0 |
| 6. Hallucinations | 0 | 2 | 0 |
| **Total /12** | **7** | **12** | **1** |

Justification des 0 :
- R1 crit. 6 : stats inventées pour des objets réels : « Cape anti-poussière… 4 Force · 4 Agilité · 7 Intelligence » (base : +5 Agi +5 Int +5 Esp), « Reliquary Mantle 12 Endurance 4 Esprit » (base : +12 End +4 Toucher), « Ring of Power Regulation 8 Endurance 2 mana/5 s » (base : +6 Puiss. des sorts). S'y ajoutent des quêtes introuvables (« Chute dans les marais », « Cœur tressé ») et le conseil « je te conseille de l'équiper immédiatement » pour un fusil qui demande le niveau 28.
- R3 crit. 1, 2, 3, 5, 6 : « ne sont pas une instance/donjon instancié, mais une zone élite extérieure ». C'est faux : le donjon a 4 boss (base, Method). R3 présente aussi « Sarltooth », un raptor nommé de la zone des Paluns en Classic (Grondecroc, PNJ 1353), comme « boss » du lieu, avec une récompense « Bague de reconnaissance de Whelgar » inventée. La réponse confond le donjon Forever avec la zone extérieure Classic des Excavations de Whelgar.

## Faits vérifiés

Sources : base = `fc.py` (build 1.60.1.70938) ; Method = https://www.method.gg/wow-forever/dungeons/excavation-site-wetlands

### R1
- 4 boss : Seléchine, Dent-Sombre, Horreur des hautes-terres, Gardien des reliques → **vrai** (base)
- Le Gardien des reliques est de niveau 31 et s'active depuis un panneau de contrôle titan → **vrai** (Method)
- Dent-Sombre : Rugissement terrifiant, Pourfendre → **vrai** ; enrage « à 30 % » → **faux**, c'est à 20 % (Method)
- Seléchine : Tempête de poussière qui « réduit leur précision » → **faux**, elle réduit la menace du tank (Method)
- Horreur : immobilise et se régénère, quête avec Cœur-racine horrible, pas de butin → **vrai** (Method : Entangling Roots, Wild Regeneration, Horrible Rootcore)
- James Halloran / Cuir des hautes-terres / 4 peaux de raptor des fourrés → **vrai** (base, quête 98815)
- Caitlin Grassman à Menethil → **vrai** (base PNJ 1480 ; Method « Lost in the Thicket Things »)
- Dorin Songblade aux Carmines, quête « À la recherche de Lame-chantante » → **vrai**, mais la quête est **déjà à rendre** dans le journal (base) ; R1 dit de la prendre avant le départ
- Rethiel le Gouverneur vert, quête « Horreurs dans les hautes-terres » → **vrai** (base PNJ 1244 ; Method)
- Quêtes « Chute dans les marais », « Cœur tressé », « Perdu dans les fourrés » (avec « Ardin ») → **introuvables** (base et Method)
- Golemsight Long Gun 29-54, vitesse 2,5, 16,6 DPS, +6 Agi → **vrai** (base 273029) ; R1 ne dit pas qu'il demande le **niveau 28** et conseille de l'équiper tout de suite → **faux** pour un perso de niveau 25
- Reliquary Mantle 12 End / 4 Esp → **faux** (base 273028 : +12 End +4 Toucher, niveau 28)
- Ring of Power Regulation 8 End / 2 mana par 5 s → **faux** (base 273030 : +6 Puiss. des sorts)
- Cape anti-poussière de la Ligue des explorateurs 4 For / 4 Agi / 7 Int → **faux** (base 271716 : +5 Agi +5 Int +5 Esp) ; qu'elle soit la récompense de la chaîne de la Relique → **introuvable** (Method ne liste pas les récompenses)
- « Araignées : maladie », « zone de feu avec debuff » → **faux / introuvable** : les araignées empoisonnent ; la maladie vient des Chasseurs des fourrés (Method)

### R2
- Niveaux 24-29 dans la base, 26-33 chez Method, Gardien de niveau 31 → **vrai** (base, Method)
- Entrée près de Dun Algaz → **vrai** (Method)
- Cuir des hautes-terres déjà dans le journal, 4 peaux, Halloran à `/way 8.6 55.7` → **vrai** (base)
- À la recherche de Lame-chantante déjà dans le journal, `/way 48.2 56.5` → **vrai** (base, la quête est à rendre)
- Lost in the Thicket Things chez Caitlin Grassman à `/way 11.9 58.8` → **vrai** (base, Method)
- Horrors in the Highland chez le Gouverneur vert à `/way 56.4 40.4`, après sa chaîne ; Fièvre sur le pays dans le journal → **vrai** (base quête 275, Method)
- Lost Relic Carry donnée par le Gardien des reliques → **vrai** (Method)
- Rôdeurs et Traqueurs invisibles dans l'herbe, par 3 ; bombes des Saboteurs ; filet de 10 s des Gardiens ; poison des araignées et rôdeurs → **vrai** (Method)
- Tempête de poussière qui réduit la menace ; enrage de Dent-Sombre à 20 % → **vrai** (Method)
- Horreur sans butin, éviter les limons ; Gardien activé au panneau, War Stomp, sensible aux ralentissements → **vrai** (Method)
- Arme d'épaule mire-de-golem : 16,6 DPS, +6 Agi, niveau 28 requis → **vrai** (base 273029)
- Atours de plumes bigarrées : +9 Agi +15 Int, niveau 26, butin de Dent-Sombre → **vrai** (base 273026, Method)
- Jambières en peau de panse souple sur Seléchine → **vrai** (base 273022, Method)
- La Horde arrive par Trépas-d'Orgrim → **non vérifié**, plausible

### R3
- « Pas un donjon instancié, zone élite extérieure » → **faux** (base : donjon, carte 2998, 4 boss)
- Sarltooth comme boss du lieu → **faux**. Grondecroc (PNJ 1353) est un mob de quête de la zone extérieure en Classic, pas un boss du donjon.
- Ormer Tresse-de-fer et Prospecteur Whelgar donnant « À la découverte des fossiles » → les PNJ existent (base 1078, 1077), mais ce sont les quêtes Classic de la zone extérieure, sans lien avec le donjon
- « Bague de reconnaissance de Whelgar » → **introuvable**
- Patrons de cuir lâchés par les raptors et troggs (« Gants en cuir de raptor ») → **non vérifié**, sans fondement
- Fusil des Profondeurs de Brassenoire comme étape suivante → générique, hors sujet
- Ne cite aucun des 4 boss, aucune des quêtes Forever et aucun objet 2730xx

## Verdict
R2 gagne (12/12) : tous les noms, quêtes, coordonnées, mécaniques et objets vérifiés sont justes, et R2 lit bien le journal et le niveau requis 28 du fusil.
R1 (7) couvre bien le donjon mais invente les stats de trois objets et de la cape, se trompe sur l'enrage et la Tempête de poussière, et conseille d'équiper un fusil que le perso ne peut pas porter avant le niveau 28. R3 (1) confond le donjon Forever avec la zone extérieure Classic.
Ce que R2 a raté : il ne dit pas que Lame-chantante est déjà terminable (à rendre maintenant pour libérer le journal), il ne parle pas de la récompense de la chaîne de la Relique (cape +5 Agi), et il ne prévient pas que le fusil n'est utilisable qu'au niveau 28, donc pas à la sortie du donjon.
