# Schémas d'explication

Schémas marketing du compagnon, en PNG (2800 px de large), chacun en clair et en sombre (`-sombre`).
Les faits viennent du dépôt : `plugins/forever-companion/mcp/server.py`, les skills, `knowledge/`,
et `docs/comparaison/bilan.md` pour les notes.

| Fichier | Contenu |
|---|---|
| `1-comment-il-repond.png` | Le parcours d'une question en 4 vérifications : dépend du perso ? (capture de l'addon), donnée du jeu ? (client + QuestieDB), règle Forever ? (connaissances sourcées et datées), il manque une info ? (Wowhead ou web, puis gardé en cache local ou dans les notes). Exemple surligné : les fragments de tablette, sans web. |
| `1b-comment-il-repond-web.png` | Le même schéma ; exemple : une quête ajoutée par Forever, absente de la base, cherchée sur Wowhead puis gardée en local. |
| `1c-comment-il-repond-regle.png` | Le même schéma ; exemple : « Les GDKP sont interdits ? », réponse tirée des connaissances, sans web. |
| `2-ce-quil-sait.png` | Trois zones : ce qu'il sait sans Internet (perso, base du jeu, 60 cartes, règles Forever, notes) ; ce qu'il va chercher (Wowhead, web, gardé pour la suite) ; ce qu'il signale (quêtes Forever hors QuestieDB, butin Classic à vérifier, annonces du jour, entrées encore inconnues). |
| `3-avec-ou-sans-mcp.png` | ChatGPT ou Gemini sans accès au jeu, contre le compagnon et son serveur MCP (perso, base et cartes, règles). Notes du comparatif à l'aveugle sur les questions liées au perso : 3 à 8 sur 12 en moyenne, contre 12 sur 12 ; temps d'un outil : 0,1 à 0,3 s. |
| `4-ce-qui-reste-chez-toi.png` | Le jeu, l'addon, les SavedVariables, les fichiers du client (lus seulement) et le serveur restent sur le PC. Seuls la question et les résultats des outils partent vers l'assistant ; le web seulement si besoin. |

Limites à rappeler avec le schéma 3 : un seul tirage par question, juge de la famille Claude,
références écrites avec les mêmes sources que le compagnon (voir `docs/comparaison/bilan.md`).

## Régénérer

Les images sont produites par un générateur local, non publié : il s'appuie sur un kit de
composants privé (composant de schéma de flux). Il vit dans `schemas/.build/`, ignoré par git.
Les données des schémas sont dans `.build/diagrams.ts`. Pour régénérer :

1. lancer le serveur de dev de `.build/` (Vite, port 5191) ;
2. lancer `python3 .build/shoot.py`, qui utilise Chrome sans tête et Pillow.
