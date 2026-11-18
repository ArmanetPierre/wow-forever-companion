# 2ᵉ série : questions complexes, résultats (18/11/2026)

Questions : `../questions-complexes.md`. Réponses brutes : `reponses/`. Réponses anonymisées,
verdicts détaillés (faits vérifiés un par un) et clé du tirage : `juge/`.

## Conditions

- **Compagnon** : plugin 0.10.0 (version du dépôt, appelée par Bash), perso réel capturé il y a
  22 h. Il lit le perso lui-même : aucune fiche n'est collée.
- **ChatGPT** : offre gratuite, sélecteur « Auto », chat éphémère, recherche web faite à chaque
  question.
- **Gemini** : « Gemini Auto », recherche web sur 3 questions sur 6.
- ChatGPT et Gemini reçoivent la fiche du perso collée avant la question (condition B de la 1ʳᵉ
  série).
- **Un juge par question**, à l'aveugle, sur 3 réponses mélangées. Le juge vérifie au moins 6 à 10
  faits par réponse, dans la base du client et sur le web. La grille sur 12 est adaptée aux plans :
  - justesse des faits ;
  - pas de confusion Classic ;
  - qualité du plan ;
  - prise en compte du perso ;
  - honnêteté sur l'incertitude ;
  - hallucinations.

## Notes sur 12

| # | Question | Compagnon | ChatGPT | Gemini |
|---|---|---|---|---|
| C13 | Monter l'ingénierie au moindre coût | **10** | 5 | 8 |
| C14 | Suite de quêtes jusqu'au niveau 30 | **12** | 5 | 5 |
| C15 | Stratégie d'Excavations : les Paluns | **12** | 7 | 1 |
| C16 | Se faire de l'or avec ses métiers | **11** | 6 | 3 |
| C17 | Organiser deux persos | **11** | 8 | 7 |
| C18 | Prêt pour les donjons en groupe | **12** | 10 | 3 |
| | **Moyenne** | **11,3** | **6,8** | **4,5** |

Sur les questions de stratégie, l'écart est **plus grand** qu'en 1ʳᵉ série :
- compagnon 11,3 contre 11,8 ;
- ChatGPT 6,8 contre 8,6 avec la fiche ;
- Gemini 4,5 contre 8,2 avec la fiche.

Plus la réponse est longue, plus les généralistes ont d'occasions d'inventer.

## Ce qui départage, question par question

- **C13, ingénierie.** Le compagnon est le seul à voir que le perso a déjà deux métiers principaux
  et doit en oublier un. Il n'invente aucun prix d'HV, mais son parcours de montée est un souvenir
  Classic à vérifier, avec deux poudres mal placées. **Gemini cite de vraies nouveautés Forever
  que le compagnon ignore** (Reagent Bot, Repair Bot, Fritz Fizzle et la Faveur des marchands).
  ChatGPT présente une route Classic comme « vérifiée sur les données Forever ».
- **C14, quêtes jusqu'au 30.** Le compagnon part du vrai journal :
  - les 13 rendus avec PNJ et `/way` ;
  - les quêtes grises à abandonner ;
  - les 14 quêtes du Bois de la Pénombre ;
  - le donjon de la tranche.

  ChatGPT bâtit une étape sur un PNJ de niveau 45 placé dans la mauvaise zone. Gemini annonce
  « +50 % d'XP en donjon » sans source et envoie le perso à Gnomeregan (29-38).
- **C15, Excavations.** Le compagnon est juste sur tous les points vérifiés : quêtes, mécaniques,
  loot de chasseur avec stats. ChatGPT a la bonne structure mais invente les stats de quatre
  objets et un seuil d'enrage. Gemini affirme que ce n'est pas un donjon et en fait un boss Classic.
- **C16, or.** Le compagnon lit les sacs et voit le plafond 150 du Dépeçage. Il conseille à tort
  de vendre une arbalète qui serait une amélioration au niveau 26. Les généralistes restent
  génériques ; Gemini invente des recettes.
- **C17, deux persos.** Dans Forever, les potions de soins sont des recettes de Secourisme. Seul
  le compagnon le sait ; les deux autres appliquent la règle Classic (alchimie). Il relie aussi
  les persos par des recettes réelles : un élixir du prêtre entre dans des gants du chasseur. Il
  se trompe en conseillant le Travail du cuir en Expert « tout de suite », alors qu'il faut 125 et
  que le perso est à 106.
- **C18, talents et équipement.** Le compagnon a les vrais talents (16 points, dont 13 en Précision), les
  vraies améliorations et les règles Forever de rotation. ChatGPT est juste mais générique : il le
  dit lui-même, il ne connaît pas les talents. Gemini invente des talents et des sorts.

## Temps de réponse

| | Durée par question | Remarque |
|---|---|---|
| Gemini | 8 à 22 s | le plus rapide ; c'est aussi le moins fiable |
| ChatGPT | 23 à 99 s | réfléchit longtemps sur les plans (C13 : 42 s de réflexion) |
| Compagnon | 45 à 110 s de bout en bout | dont 30 à 92 s d'outils et de recherche ; C15 a demandé environ 40 appels d'outils |

Sur ces questions, **le compagnon est le plus lent**. Une bonne part vient de données qui
manquent : il les cherche à tâtons, par exemple en passant 14 itemId en revue pour trouver le loot
de C15.

## Limites

- Le juge est un modèle Claude, comme le compagnon. Il vérifie les faits dans la même base locale
  que le compagnon : cela favorise le compagnon sur les faits du client, pas sur les faits du web.
- Un seul tirage par question. Le compagnon a été lancé en sous-agent, avec le texte de l'agent et
  des skills chargés à la main.
- **Biais d'anonymisation.** Dans la réponse C13 de ChatGPT, mon remplacement automatique a laissé
  un « [perso] » qui ne figurait pas dans l'original, et le juge le lui reproche. L'effet est
  probablement d'un point au plus.
- Six questions écrites par nous, sur un perso que nous connaissons.

## Ce que la série a appris sur l'outil

Les sous-agents du compagnon ont dit ce qui leur manquait. Le juge a relevé ses erreurs. Par
ordre d'impact :

1. **Formateurs de métier** : ni palier suivant, ni compétence requise (125 pour Expert), ni nom
   et `/way` du formateur. Ce manque est à l'origine de l'erreur de C17 et des « à vérifier » de
   C13 et C16.
2. **Parcours de montée d'un métier** : la base estime mal le rang des recettes d'un métier non
   appris (≈5 pour des recettes de haut niveau), sans couleur ni quantités. C'est la faiblesse de
   C13.
3. **Contenu Forever des métiers** : les recettes et vendeurs ajoutés par Forever manquent à la
   base de connaissances. Gemini les a trouvés sur le web.
4. **Donjons** : `dungeon` ne donne que les noms des boss. Il manque le loot par boss, les quêtes du
   donjon et les mécaniques. `search` ne trouve pas un objet par son nom anglais.
5. **Bug** : `quests disponibles` avec un nom de zone en français (« Bois de la Pénombre ») renvoie
   0 quête, alors que « Duskwood » en renvoie 14.
6. **Prix** : aucun prix de l'HV ni prix marchand. Il est impossible de comparer « vendre brut » et
   « fabriquer ».
7. **Arbres de talents** : pas d'arbre complet (rangées, prérequis), pas de nom anglais des talents.
8. **XP par quête** : sans ce chiffre, il est impossible de vérifier qu'un itinéraire mène bien au
   niveau visé.

**Corrigé le 18/11/2026 (plugin 0.10.0)** : points 1, 2, 4, 5, 7 et 8, ainsi que le contenu
Forever des métiers (point 3, `knowledge/metiers-forever.md`). Reste ouvert : les prix de l'HV
(point 6) ; seuls les prix marchands sont donnés. Une nouvelle série devra mesurer l'effet sur
les notes et sur le temps de réponse.

Pistes plus larges pour les joueurs avancés : `../../conception/plus-values.md`.

## 2ᵉ passage, après les correctifs (18/11/2026)

Même protocole. Le compagnon a été relancé avec les correctifs. Les réponses de ChatGPT et
Gemini sont les mêmes, rejugées par de nouveaux juges, à l'aveugle, dans un nouvel ordre
(`juge-v2/`). Réponses du compagnon : `reponses-v2/`.

| # | Question | Compagnon avant → après | ChatGPT (mêmes réponses) | Gemini (mêmes réponses) |
|---|---|---|---|---|
| C13 | Ingénierie | 10 → **6** | 5 → 10 | 8 → 7 |
| C14 | Quêtes jusqu'au 30 | 12 → **12** | 5 → 4 | 5 → 3 |
| C15 | Excavations | 12 → **11** | 7 → 7 | 1 → 1 |
| C16 | Or avec les métiers | 11 → **11** | 6 → 8 | 3 → 4 |
| C17 | Deux persos | 11 → **11** | 8 → 6 | 7 → 5 |
| C18 | Donjons en groupe | 12 → **12** | 10 → 8 | 3 → 2 |
| | **Moyenne** | 11,3 → **10,5** | 6,8 → 7,2 | 4,5 → 3,7 |

**Le bruit du juge est grand.** ChatGPT et Gemini ont rendu les mêmes réponses, et leurs notes
bougent quand même de 1 à 5 points (C13 : ChatGPT passe de 5 à 10). Un écart d'un point ou deux
sur une question n'est donc pas significatif.

**Ce qui a vraiment changé :**
- **Temps : 34 à 75 s** de bout en bout, contre 45 à 110 s. **Appels d'outils : 6 à 12**, contre
  jusqu'à 40 pour C15. Le butin des donjons en un appel et la zone en français y sont pour
  beaucoup.
- **Les deux erreurs de la 1ʳᵉ série ont disparu** : plus d'Expert de Travail du cuir conseillé
  « tout de suite », et le palier bloqué est dit (« pas encore : 106/125 »). L'arme à garder
  pour le niveau 26 est bien jugée.
- **C13 recule, à cause du nouveau parcours de métier.** Il fait passer par des recettes déjà
  grises (balles fabriquées à 70-81, 117-140 et 175-221, poudre dense jusqu'à 297). Le juge le
  dit « pas utilisable tel quel ». ChatGPT, qui suit le guide Wowhead Forever, gagne cette question.
  Le compagnon reste le seul à voir qu'il faut d'abord abandonner un des deux métiers principaux.

**Nouveaux trous signalés par le compagnon et les juges :**
1. **Parcours de métier** :
   - couleurs mal estimées, donc des recettes grises dans le parcours ;
   - aucune recette proposée depuis 1 en Couture et en Alchimie ;
   - le parcours ne prévient pas quand le perso a déjà deux métiers principaux ;
   - totaux non ramenés aux matières brutes ;
   - les métiers de récolte (Herboristerie, Dépeçage) reçoivent des « recettes » au lieu de zones
     de récolte et de niveaux de mobs.
2. **Guide de donjon** :
   - *Highland Hides* demande des peaux de raptor des fourrés, pas de crocilisque ;
   - le point de rendu de *Lame-chantante* est faux (Paluns, pas Carmines) ;
   - l'entrée et le trash dangereux manquent.
3. **Talents** : il manque l'effet par rang et les prochains sorts à apprendre.
4. **Itinéraire de leveling** sur plusieurs zones jusqu'à un niveau cible : il n'existe pas, le
   compagnon interroge les zones une à une.
5. **Divers** :
   - le coût des formations ;
   - les recettes connues ;
   - la réputation requise chez un vendeur ;
   - le royaume des persos dans `characters` ;
   - une quête d'Arathi listée aux Paluns.
