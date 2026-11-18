# Observations pendant le comparatif (18/11/2026)

Notes prises en posant les 48 prompts à ChatGPT et Gemini. Elles complètent les notes du juge.
ChatGPT et Gemini sont de vrais concurrents : un joueur les a déjà sous la main.

## Ce que les concurrents font bien

- **Vitesse.** ChatGPT répond en 10 à 20 s, recherche web comprise, et le texte s'affiche au
  fil de l'eau. Gemini est du même ordre. Le compagnon passe 0,1 à 0,3 s dans les outils. Ce
  qui prend du temps, c'est le modèle dans Claude Code : il réfléchit, appelle les outils,
  puis rédige.
- **Visuels.** ChatGPT insère une carte quand il y a un lieu à montrer (entrée de la Drowned
  City, avec trois repères). Gemini insère une vidéo YouTube (Éolides). Les deux ajoutent des
  tableaux et des boutons de suite (« Je l'ai / Je ne l'ai pas », « Optimiser mes 44 points »).
  C'est parlant pour un joueur.
- **Actualité.** Deux semaines après la sortie, le web couvre déjà Forever. Les deux trouvent
  les annonces importantes : GDKP, rulesets, raids du 9/12, Onyxia, Éolides. Sur ces
  questions, l'écart avec nous est faible.
- **Relances.** Ils posent une question de suivi quand il manque une info (rangs du familier,
  noms des 13 quêtes). Le compagnon n'en a pas besoin pour le perso, puisqu'il lit la capture.

## Où ils décrochent (premier survol, à confirmer par le juge)

- Ce qui dépend du perso : ils n'ont que ce qu'on leur colle. Sans la fiche (prompts A), ils
  devinent. Avec la fiche (prompts B), ils s'améliorent nettement, mais il faut l'écrire à la
  main à chaque fois.
- Le détail du jeu : noms de quêtes, de PNJ et de lieux inventés ou mélangés ; coordonnées qui
  diffèrent d'une réponse à l'autre ; mécaniques Classic confondues (points de dressage et
  talents ; carreaux pour une arbalète).
- La constance : la même question, posée deux fois, donne des dates et des seuils différents.
- Le cadre : Gemini a présenté une fois Forever comme un « serveur privé WotLK 3.3.5 ».
- La mémoire de ChatGPT déborde : même en chat éphémère, il a utilisé l'historique du compte.

## Pistes pour le compagnon

1. **Une carte avec un repère.** Quand une réponse contient un `/way`, produire une petite
   image de la carte de la zone avec le point. Les cartes sont dans le client (lecture seule,
   déjà autorisée) ; il suffit de les découper et d'y poser un repère, en local. C'est le plus
   gros écart visuel, et nous avons des coordonnées plus fiables qu'eux.
2. **Le temps de réponse.** Mesurer le temps total réel d'une question dans Claude Code, et
   pas seulement le temps des outils. Pistes : `overview` déjà précalculé à la synchro (fait),
   skills plus courtes, modèle plus rapide pour les questions simples.
3. **Les suites proposées.** Finir une réponse par une ou deux suites concrètes (« Je te trace
   le chemin vers Whelgar ? »), sans remplissage.
4. **Les tableaux.** Les garder pour les comparaisons (objets, raids) ; ils se lisent mieux
   qu'une liste.
5. **Le message marketing.** Ne pas dire « ChatGPT se trompe sur tout » : c'est faux sur
   l'actualité. Dire plutôt : « Il connaît les annonces. Le compagnon connaît ton perso, tes
   quêtes et la base du jeu, et il ne se contredit pas. »
