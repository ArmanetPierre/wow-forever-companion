# Bilan franc : compagnon, ChatGPT, Gemini (18/11/2026)

Ce bilan rassemble, sans enjoliver, les notes du juge à l'aveugle (`resultats.md`), les
observations faites en posant les questions (`observations.md`) et un chronométrage du compagnon.

## Le verdict en une phrase

ChatGPT est un très bon concurrent. Il est gratuit, disponible partout, aussi juste que nous sur
l'actualité de Forever, et il illustre ses réponses. Le compagnon gagne nettement sur tout ce qui
touche au perso et au détail du jeu (quêtes, coordonnées, familier, objets), car il lit le perso et
la base du client au lieu de deviner. Le reste de l'écart est plus faible qu'il n'y paraît.

## Question par question

Notes du juge sur 12. « Sans fiche » : la question brute. « Avec fiche » : la même question
précédée d'une description du perso écrite à la main.

| # | Question | Compagnon | Meilleur ChatGPT | Meilleur Gemini | Qui gagne, et pourquoi |
|---|---|---|---|---|---|
| C01 | Je fais quoi maintenant ? | 12 | 8 (avec fiche) | 8 (avec fiche) | **Compagnon, net.** Lui seul voit les 13 quêtes à rendre dans le journal plein. ChatGPT sans fiche propose un circuit de zones Classic avec des quêtes introuvables dans les données du jeu. |
| C02 | Arbalète ou fusil ? | 12 | 10 (avec fiche) | 11 (avec fiche) | **Compagnon, de peu.** Avec la fiche, Gemini voit lui aussi le niveau 26 et la compétence à 1/125. ChatGPT sans fiche surestime le gain (« +15 % » au lieu d'environ +5,6 %). |
| C03 | Fragments de la quête | 12 | 5 (sans fiche) | 5 (avec fiche) | **Compagnon, très net.** ChatGPT invente des coordonnées « relevées dans les bases ». Gemini invente l'objet à fouiller ; sans fiche, il fait de Forever un serveur privé WotLK. |
| C04 | Familier : nourriture et dressage | 12 | 9 (avec fiche) | 7 (avec fiche) | **Compagnon, net.** Lui seul calcule les points de dressage (120, dont 44 libres) et protège les ingrédients gardés pour une quête. Gemini sans fiche confond dressage et talents. |
| C05 | XP des donjons depuis le correctif | 12 | 6 | 8 (sans fiche) | **Compagnon.** Les généralistes trouvent le correctif mais se contredisent sur les dates et les seuils. Gemini avec fiche dit encore « le farm d'instances reste très efficace ». |
| C06 | Krol'dok | 12 | 7 | 10 (avec fiche) | **Compagnon.** L'entrée n'est pas encore connue. ChatGPT, dans les deux cas, et Gemini sans fiche inventent des coordonnées ; Gemini avec fiche s'en sort bien. |
| C07 | Raids du 9 décembre | 12 | 10 (sans fiche) | 8 | **Proche.** Tous trouvent l'annonce. Le compagnon ajoute le `/way` et évite le piège du Cœur du Magma. |
| C08 | GDKP | 12 | 10 (sans fiche) | 9 (avec fiche) | **Proche.** Tout le monde répond « interdit ». Gemini sans fiche se trompe sur les loots réservés (HR). |
| C09 | Normal et JcJ dans un donjon | 11 | 10 (avec fiche) | 10 (avec fiche) | **Quasi égalité.** |
| C10 | Éolides | 12 | 11 (les deux) | 11 (sans fiche) | **Égalité.** ChatGPT est juste et sourcé ; le compagnon est seulement plus court. |
| C11 | Drowned City (EN) | 12 | 11 (avec fiche) | 10 (avec fiche) | **Quasi égalité.** ChatGPT montre une carte avec trois repères. |
| C12 | Onyxia par perso (EN) | 11 | 10 (sans fiche) | 8 (sans fiche) | **Proche.** Gemini avec fiche plaque la chaîne Classic de 16 quêtes. |

**Moyennes** : compagnon 11,8. ChatGPT 7,8 sans fiche et 8,6 avec. Gemini 6,1 sans fiche et 8,2
avec.
**Questions liées au perso (C01-C04)** : 12 contre 3 à 8.
**Actualité de Forever (C07-C12)** : compagnon 11,7, meilleur généraliste 8 à 11 selon la
question ; l'écart y est faible.

## Temps de réponse

| | Temps mesuré ou observé | Ce que voit le joueur |
|---|---|---|
| ChatGPT (gratuit, recherche web) | environ 10 à 20 s, **observé** lors des 48 questions, sans chronomètre | Le texte s'affiche tout de suite, au fil de l'eau ; parfois une carte ou un tableau. |
| Gemini (Auto, recherche web) | même ordre, **observé**, sans chronomètre | Pareil ; parfois une vidéo. |
| Compagnon avec Opus | 12,9 s (GDKP) ; 23,9 s (« Je fais quoi ? ») | Les appels d'outils d'abord, puis le texte. |
| Compagnon avec Sonnet | 10,0 s (GDKP) ; 11,9 s (« Je fais quoi ? ») | Pareil. |
| Compagnon avec Haiku | 15,7 s (GDKP) ; 11,7 s (« Je fais quoi ? ») | Pareil. |

Comment le compagnon a été chronométré :
- le 18/11/2026, dans Claude Code, du début à la réponse finale, appels aux outils compris ;
- sur un vrai perso capturé, sans recherche web ;
- un seul essai par cas : ce sont des ordres de grandeur ;
- avec la version du plugin installée dans cette session, qui précède l'optimisation.

**Ce que ça veut dire, franchement.** En temps brut, l'écart est faible : 10 à 24 s contre 10 à
20 s. L'impression que ChatGPT est plus rapide vient surtout de l'affichage :
- il écrit dès la première seconde ;
- le compagnon réfléchit et appelle ses outils avant d'écrire ;
- Opus est le plus lent sur une question large (24 s) ;
- Sonnet donne des réponses de même qualité en 10 à 12 s.

## Avantages et inconvénients

### ChatGPT

| Avantages | Inconvénients |
|---|---|
| Gratuit, sans installation, sur téléphone, avec la voix. | Ne connaît pas le perso. Il faut le décrire à chaque question, et ça reste approximatif. |
| Le texte s'affiche tout de suite. | Invente des quêtes, des PNJ et des coordonnées quand il ne sait pas (C01, C03, C06). |
| Très bon sur l'actualité grâce au web (C07, C08, C10, C11 : 10 à 11 sur 12). | Change de dates et de seuils d'une conversation à l'autre (C05). |
| Cartes, tableaux, boutons de suite : c'est parlant. | Utilise l'historique du compte même en chat éphémère : utile, mais pas maîtrisé. |
| Pose une question quand il manque une info. | Plaque parfois des règles Classic sur Forever. |

### Gemini

| Avantages | Inconvénients |
|---|---|
| Gratuit, rapide, intégré à l'écosystème Google. | Le moins fiable sans fiche (6,1) : 3 pièges Classic et 3 inventions graves sur 12 questions. |
| Vidéos YouTube pertinentes (Éolides). | A présenté Forever comme un « serveur privé WotLK 3.3.5 ». |
| Avec la fiche, il progresse beaucoup (8,2) : très bon sur C02 et C06. | Confond des mécaniques de base (points de dressage et talents, « carreaux » pour une arbalète). |

### Compagnon

| Avantages | Inconvénients |
|---|---|
| Lit le vrai perso (quêtes, sacs, familier, équipement) : rien à recopier. | Il faut Claude Code et un abonnement payant ; ChatGPT est gratuit. |
| Base du client : quêtes, objets et `/way` exacts, et maintenant une carte avec repères. | Il faut installer l'addon et synchroniser en jeu (Ctrl+Maj+S). |
| Aucun piège Classic ni aucune invention grave sur les 12 questions. | Pas sur téléphone, pas de voix : il se sert à l'ordinateur. |
| Dit « inconnu » au lieu d'inventer (entrée de Krol'dok). | L'actualité dépend de sa base de connaissances, qu'il faut tenir à jour. Pour une annonce toute fraîche, ChatGPT est souvent devant. |
| Constant d'une fois à l'autre. | La réponse s'affiche moins vite. Opus est lent sur les questions larges. |

## Limites de ce bilan

- **Le juge.** Il est de la même famille que le compagnon (Claude). Il note des références que j'ai
  écrites avec les mêmes sources que le compagnon : le 11,8 est donc flatté. L'écart sur les
  questions liées au perso, lui, tient sans ces références.
- **Les temps de ChatGPT et Gemini** n'ont pas été chronométrés, seulement observés.
- **Un seul tirage par question**, offres gratuites, le 18/11/2026.
- Pour un chiffre public, il faudra un second juge, humain ou d'un autre fournisseur.

## Ce qu'on peut dire publiquement sans mentir

> ChatGPT connaît les annonces. Le compagnon connaît ton perso, tes quêtes et la base du jeu : il
> te dit quoi rendre, où cliquer, et il n'invente pas.

À éviter : « plus rapide que ChatGPT » (faux) et « ChatGPT se trompe sur tout » (faux sur
l'actualité).
