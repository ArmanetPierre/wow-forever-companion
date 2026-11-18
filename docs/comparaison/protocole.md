# Comparatif : compagnon Forever vs ChatGPT vs Gemini — protocole

Objectif : produire des exemples **honnêtes et vérifiables** de ce que le compagnon apporte par
rapport à un assistant généraliste. Le protocole est fait pour qu'un lecteur sceptique puisse
refaire l'expérience et obtenir les mêmes conclusions.

## 1. Les répondants

| Code | Répondant | Ce qui est noté au moment du test |
|---|---|---|
| **CMP** | Compagnon WoW Forever (plugin 0.9.0, addon 1.4.0), dans Claude Code | version du plugin, date de la capture du perso, outils appelés |
| **GPT** | ChatGPT (application web ou mobile, réglages par défaut) | nom exact du modèle affiché, offre (gratuite / Plus), recherche web activée ou non |
| **GEM** | Gemini (application web, réglages par défaut) | nom exact du modèle affiché, offre, recherche web (« Google Search ») activée ou non |

- **Même date pour tous**, sur une seule journée. Noter la date et l'heure de chaque réponse.
- **Recherche web** : on garde le comportement **par défaut** du produit, ce qu'un joueur aurait.
  On note pour chaque réponse si une recherche a été faite (sources affichées ou non).
- **Une nouvelle conversation par question**, sans mémoire ni instructions personnalisées
  (désactiver la mémoire de ChatGPT et les « Gems » / instructions de Gemini, ou utiliser un
  compte sans historique).
- **Pas de relance** : on garde la première réponse complète. Si le produit pose une question
  de clarification, on répond une seule fois avec le contexte B (voir plus bas) et on le note.

## 2. Les deux conditions pour GPT et GEM

| Condition | Ce qu'on colle | Pourquoi |
|---|---|---|
| **A — brute** | la question telle qu'un joueur la tape | ce qu'obtient un joueur pressé |
| **B — avec contexte** | un paragraphe « mon perso » + la question | équitable : un joueur qui décrit son perso ; mesure ce qui reste quand le contexte est donné |

Le contexte B décrit **Brannok**, un perso fictif dont les valeurs reprennent exactement un
vrai perso capturé par l'addon (Nain Chasseur 25, Alliance, ruleset PvP, Les Paluns…). Le
compagnon, lui, lit ces valeurs directement par l'addon : il répond **sans** qu'on les colle.

Les textes exacts sont dans `prompts-a-coller.txt` (24 textes : 12 en A, 12 en B).

Le compagnon répond une seule fois par question (il n'a pas besoin de la condition B).
Ses réponses sont dans `reponses/compagnon.md`.

## 3. Les questions

12 questions vitrines (`questions.md`), tirées de `docs/evals/banque-questions.md` :
- 6 **faits propres à Forever**, où la réponse Classic est fausse et vérifiable (XP des donjons,
  nouveaux donjons, raids du 9/12, GDKP, rulesets, Éolides) ;
- 4 **questions liées au perso** (quoi faire, arbalète ou fusil, quête précise avec `/way`,
  familier) ;
- 2 **questions en anglais**.

Chaque question a une **réponse de référence vérifiée** (faits, sources, `/way`) qui sert au juge.

## 4. Notation à l'aveugle

1. Copier chaque réponse dans `reponses/gpt-A.md`, `gpt-B.md`, `gem-A.md`, `gem-B.md` (même
   format que `reponses/compagnon.md` : un titre par question, la réponse brute).
2. **Anonymiser** : pour chaque question, mélanger les 5 réponses (CMP, GPT-A, GPT-B, GEM-A,
   GEM-B) et leur donner les lettres R1 à R5 au hasard (tirage noté dans un fichier `cle.md` que
   le juge ne voit pas). Retirer tout ce qui trahit l'auteur :
   - badges `[Forever · …]`, « capture », « Ctrl+Maj+S », noms d'outils, nom du perso (« Brannok »)
     → remplacés par `[source]`, `[perso]` ;
   - mentions « en tant qu'IA », liens cliquables (garder le nom du site), mise en forme propre à
     un produit.
   Le fond (chiffres, noms, `/way`, faits) n'est **jamais** modifié.
3. **Juge** : un modèle qui n'a répondu à aucune question (par exemple un autre fournisseur, ou
   un humain), avec le prompt de `juge.md`, la question, la référence et les 5 réponses anonymes.
   Idéalement deux juges (un modèle + un joueur humain) ; en cas d'écart de plus d'un point sur
   un critère, on retient la note la plus basse et on le signale.

### Grille (6 critères, 0 à 2, total sur 12)

| Critère | 2 | 1 | 0 |
|---|---|---|---|
| **Justesse Forever** | tous les faits clés de la référence sont présents et justes | une partie seulement, ou un fait clé manque | un fait clé est faux ou contredit la référence |
| **Pas de confusion Classic** | aucune info Classic/Retail présentée comme vraie dans Forever ; les infos Classic sont signalées comme telles | une info Classic non signalée mais sans conséquence sur le conseil | le conseil principal repose sur une règle Classic fausse dans Forever |
| **Précision actionnable** | noms exacts (PNJ, objets, quêtes), chiffres, `/way` ou lieu précis quand la question s'y prête | conseil utile mais vague (« au nord », « un PNJ de la zone ») | rien d'actionnable, ou des noms/coordonnées inventés |
| **Prise en compte du perso** | la réponse s'appuie sur le niveau, la classe, l'équipement, les quêtes ou le familier réels | prise en compte partielle ou générique (« à ton niveau… ») | ignore le perso, ou conseil inadapté à son niveau ou sa faction ; pour une question générale sans lien au perso : 2 si rien ne contredit le perso |
| **Concision et ton** | la réponse tient en ~150 mots ou moins pour une question simple, verdict d'abord, pas de remplissage | correcte mais longue ou verdict noyé | verbeuse, hors sujet, ou sans réponse claire |
| **Hallucinations** | aucune invention | une invention mineure (détail faux sans effet sur le conseil) | une invention qui change le conseil (quête, PNJ, donjon, règle ou chiffre inexistant) |

Règle stricte : un critère sans élément pour juger reçoit **1**, pas 2. Chaque note 0 est
justifiée par une citation courte de la réponse.

## 5. Ce qu'on publie

- Le tableau des moyennes par répondant et par critère, pour les 12 questions.
- 3 ou 4 **exemples côte à côte** choisis par le juge (« extrait remarquable »), y compris un
  exemple où un généraliste fait aussi bien ou mieux, s'il existe.
- Les prompts, la référence et les réponses complètes, pour que tout soit vérifiable.
- La date, les versions des modèles et les réglages de recherche web.

## 6. Limites (à publier avec les résultats)

- **Petit échantillon** : 12 questions choisies parce qu'une erreur y est facile. Ce n'est pas
  un échantillon représentatif de toutes les questions de joueurs.
- **Avantage structurel** : le compagnon lit les données du perso et une base locale tirée du
  client du jeu. La condition B compense une partie de cet écart, pas tout (pas de base d'objets
  ni de coordonnées chez les généralistes).
- **Références en partie issues de nos propres sources** : les `/way` et les données de quêtes
  viennent de QuestieDB et du client du jeu, que le compagnon utilise aussi. Les faits généraux
  (raids, rulesets, GDKP, XP) sont sourcés par Blizzard ou la presse et vérifiables
  indépendamment. Les références marquées « probable » sont notées avec indulgence (une réponse
  qui donne la même info avec la même prudence obtient 2).
- **Fraîcheur** : Forever est sorti le 04/11/2026 ; certains faits (XP, bugs) bougent. Une
  réponse qui cite une info plus récente et sourcée que la référence n'est pas pénalisée.
- **Le compagnon a été réglé sur des questions proches** (banque de 72 questions) : les 12
  questions en sont tirées. C'est un test de démonstration, pas une évaluation indépendante.
- **Variabilité** : les généralistes donnent des réponses différentes d'un essai à l'autre. Pour
  un résultat plus solide, poser chaque question 3 fois et noter la moyenne.
