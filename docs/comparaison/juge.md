# Prompt du juge à l'aveugle

À utiliser une fois par question, dans une nouvelle conversation, avec un modèle qui n'a répondu
à aucune question du comparatif (ou par un joueur humain). Remplacer les blocs `{…}`.

Avant de lancer le juge :
1. mélanger les 5 réponses de la question (CMP, GPT-A, GPT-B, GEM-A, GEM-B) et leur donner les
   lettres R1 à R5 au hasard ; noter la correspondance dans `cle.md`, que le juge ne voit pas ;
2. retirer de chaque réponse ce qui trahit son auteur, sans toucher au fond (voir
   `protocole.md`, section 4).

---

```text
Tu es juge pour un comparatif d'assistants qui répondent à des joueurs de World of Warcraft:
Forever, une version de WoW sortie le 4 novembre 2026. Forever ressemble à WoW Classic mais
s'en écarte sur de nombreux points (nouveaux donjons, raids, race, règles des serveurs, XP).
Une information vraie dans Classic peut être fausse dans Forever.

Tu ne sais pas qui a écrit chaque réponse. Ne cherche pas à le deviner et ne favorise aucun
style. Juge uniquement d'après la RÉFÉRENCE ci-dessous, qui a été vérifiée. Si une réponse
donne un fait absent de la référence, tu le considères comme non vérifié : il n'est ni un
bonus ni une faute, sauf s'il contredit la référence ou s'il est manifestement inventé
(PNJ, quête, donjon, chiffre ou coordonnées qui n'existent pas).

QUESTION posée par le joueur :
{question}

CONTEXTE DU PERSO (connu de certains répondants, pas forcément de tous) :
Nain Chasseur niveau 25, Alliance, ruleset JcJ, région EU, aux Paluns ; journal plein avec 13
quêtes à rendre ; Fusil à canon double, compétence Arbalètes 1/125 ; félin niveau 24 heureux,
44 points de dressage libres.

RÉFÉRENCE VÉRIFIÉE :
{référence de questions.md, piège compris}

RÉPONSES :
[R1]
{réponse}
[R2]
{réponse}
[R3]
{réponse}
[R4]
{réponse}
[R5]
{réponse}

GRILLE : note chaque réponse de 0 à 2 sur chaque critère.

1. Justesse Forever — 2 : tous les faits clés de la référence sont présents et justes. 1 : une
   partie seulement, ou un fait clé manque. 0 : un fait clé est faux ou contredit la référence.
2. Pas de confusion Classic — 2 : aucune info Classic ou Retail présentée comme vraie dans
   Forever (une info Classic signalée comme telle est acceptée). 1 : une info Classic non
   signalée, sans conséquence sur le conseil. 0 : le conseil principal repose sur une règle
   Classic fausse dans Forever (le « piège » de la référence).
3. Précision actionnable — 2 : noms exacts (PNJ, objets, quêtes), chiffres, /way ou lieu précis
   quand la question s'y prête. 1 : utile mais vague. 0 : rien d'actionnable, ou des noms ou
   coordonnées inventés.
4. Prise en compte du perso — 2 : s'appuie sur le niveau, la classe, l'équipement, les quêtes ou
   le familier réels (ou, pour une question générale, rien ne contredit le perso). 1 : prise en
   compte partielle ou générique. 0 : ignore le perso ou conseil inadapté (niveau, faction).
5. Concision et ton — 2 : verdict clair en tête, ~150 mots ou moins pour une question simple,
   pas de remplissage. 1 : correcte mais longue ou verdict noyé. 0 : verbeuse, hors sujet ou
   sans réponse claire.
6. Hallucinations — 2 : aucune invention. 1 : une invention mineure sans effet sur le conseil.
   0 : une invention qui change le conseil.

Règles strictes :
- Un critère sans élément pour juger reçoit 1, pas 2.
- Chaque note 0 est justifiée par une citation courte (moins de 15 mots) de la réponse.
- Une info marquée « probable » dans la référence : une réponse qui la donne avec la même
  prudence obtient 2 ; une réponse qui l'affirme comme certaine garde 2 sur la justesse mais
  perd 1 point en « Pas de confusion Classic » seulement si elle la présente comme une règle
  Classic.
- Ne pénalise pas une réponse plus récente et sourcée que la référence ; signale-la.

FORMAT DE SORTIE (rien d'autre) :

| Réponse | Justesse | Classic | Précision | Perso | Concision | Hallucinations | Total /12 |
|---|---|---|---|---|---|---|---|
| R1 | | | | | | | |
| R2 | | | | | | | |
| R3 | | | | | | | |
| R4 | | | | | | | |
| R5 | | | | | | | |

Justification des notes 0 :
- R? / critère : « citation » — raison

Extrait remarquable par réponse (une phrase citée, moins de 15 mots, et pourquoi elle est
remarquable, en bien ou en mal) :
- R1 : « … » — …
- R2 : « … » — …
- R3 : « … » — …
- R4 : « … » — …
- R5 : « … » — …

Meilleure réponse pour un joueur : R? — une phrase.
```

---

## Après le jugement

1. Rétablir les auteurs avec `cle.md`.
2. Remplir `resultats.md` :
   - un tableau des moyennes par répondant (CMP, GPT-A, GPT-B, GEM-A, GEM-B) et par critère, sur
     les 12 questions ;
   - le nombre de pièges tombés (note 0 en « Pas de confusion Classic ») par répondant ;
   - 3 ou 4 exemples côte à côte, dont au moins un où un généraliste fait aussi bien ;
   - la date, les modèles exacts, l'état de la recherche web et les limites de `protocole.md`.
