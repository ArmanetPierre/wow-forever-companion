# Résultats du comparatif — compagnon, ChatGPT, Gemini (18/11/2026)

## Conditions

- **Répondants** (5 par question) :
  - CMP : le compagnon (plugin 0.9.0, base locale, aucune recherche web) ;
  - GPT-A / GPT-B : ChatGPT, offre gratuite, modèle par défaut, recherche web active, chat éphémère ;
  - GEM-A / GEM-B : Gemini, mode « Auto », recherche web active, activité désactivée.
- **A** : la question brute. **B** : la même question précédée de la fiche du perso, écrite à la main.
- **Juges** : trois instances de Claude Sonnet, à l'aveugle. Les 5 réponses de chaque question
  sont mélangées et anonymisées (`juge/C01.md`…), la clé du tirage est dans `juge/cle.md`
  (graine 20261118). Grille de `juge.md` : 6 critères notés de 0 à 2, total sur 12. Verdicts
  détaillés : `juge/verdict-C01.md`…

## Notes par question (sur 12)

| Question | CMP | GPT-A | GPT-B | GEM-A | GEM-B |
|---|---|---|---|---|---|
| C01 Je fais quoi ? | **12** | 4 | 8 | 3 | 8 |
| C02 Arbalète ou fusil ? | **12** | 9 | 10 | 6 | 11 |
| C03 Fragments de la quête | **12** | 5 | 4 | 2 | 5 |
| C04 Familier | **12** | 3 | 9 | 1 | 7 |
| C05 XP des donjons | **12** | 6 | 6 | 8 | 5 |
| C06 Krol'dok | **12** | 7 | 7 | 5 | 10 |
| C07 Raids du 9/12 | **12** | 10 | 9 | 8 | 8 |
| C08 GDKP | **12** | 10 | 9 | 5 | 9 |
| C09 Normal et JcJ | **11** | 8 | 10 | 9 | 10 |
| C10 Éolides | **12** | 11 | 11 | 11 | 8 |
| C11 Drowned City (EN) | **12** | 10 | 11 | 7 | 10 |
| C12 Onyxia (EN) | **11** | 10 | 9 | 8 | 7 |

## Moyennes par critère (sur 2) et total (sur 12)

| Répondant | Justesse | Pas de Classic | Précision | Perso | Concision | Hallucinations | **Total** | Pièges tombés | Inventions graves |
|---|---|---|---|---|---|---|---|---|---|
| CMP | 2,00 | 2,00 | 1,92 | 2,00 | 1,92 | 2,00 | **11,8** | 0 | 0 |
| GPT-A | 1,25 | 1,58 | 1,08 | 1,33 | 1,17 | 1,33 | **7,8** | 1 | 2 |
| GPT-B | 1,33 | 1,83 | 1,25 | 1,92 | 0,92 | 1,33 | **8,6** | 0 | 2 |
| GEM-A | 0,83 | 1,25 | 1,00 | 1,00 | 1,08 | 0,92 | **6,1** | 3 | 3 |
| GEM-B | 1,08 | 1,58 | 1,25 | 1,92 | 1,25 | 1,08 | **8,2** | 1 | 1 |

« Pièges tombés » : nombre de 0 en « Pas de confusion Classic ». « Inventions graves » :
nombre de 0 en « Hallucinations ».

## Par type de question (total moyen sur 12)

| Type | CMP | GPT-A | GPT-B | GEM-A | GEM-B |
|---|---|---|---|---|---|
| Liées au perso (C01-C04) | **12,0** | 5,2 | 7,8 | 3,0 | 7,8 |
| Faits propres à Forever (C05-C10) | **11,8** | 8,7 | 8,7 | 7,7 | 8,3 |
| En anglais (C11-C12) | **11,5** | 10,0 | 10,0 | 7,5 | 8,5 |

## Ce qu'il faut en retenir

1. **L'écart est net sur les questions liées au perso** : 12 contre 3 à 8. Sans la fiche, les
   généralistes devinent. Avec la fiche collée à la main (B), ils progressent nettement (de
   5,2 à 7,8 pour ChatGPT, de 3,0 à 7,8 pour Gemini), sans rattraper le compagnon. Ils restent
   imprécis sur les quêtes, les coordonnées et les règles du familier.
2. **Sur l'actualité de Forever, les généralistes s'en sortent bien** : 8 à 11 sur les GDKP,
   les rulesets, les raids, les Éolides et Onyxia. Le web couvre déjà Forever deux semaines
   après la sortie.
3. **Les inventions viennent surtout du détail du jeu** : quêtes et PNJ inexistants, talents
   mal nommés, mécaniques Classic plaquées sur Forever.

## Exemples côte à côte

**C03 — « Je trouve pas les fragments de tablette, ils sont où ? »**
- Gemini (A), 2/12 : présente WoW Forever comme un serveur privé (« extension WotLK 3.3.5 »)
  et conseille de vider le dossier Cache.
- Compagnon, 12/12 : les 4 fragments, l'objet à fouiller pour chacun (Relique ancienne ou Terre
  meuble), un `/way` par fragment, puis le `/way` de Whelgar.

**C04 — « Mon félin : je lui donne quoi et je mets où mes points de dressage ? »**
- Gemini (A), 1/12 : confond points de dressage et points de talent, et propose un arbre
  Maîtrise des bêtes.
- Compagnon, 12/12 : il voit dans les sacs les 3 ingrédients gardés pour la *Goulash des
  Carmines* et dit de ne pas les donner. Il calcule les 120 points (44 libres), lit les rangs de
  Griffe et de Morsure, et signale que le Foie de Broche-tripes (niveau 12) est trop bas.

**C01 — « Je fais quoi maintenant ? »**
- ChatGPT (A), 4/12 : un circuit en 7 étapes, dont 5 quêtes introuvables dans les données du
  jeu, sans un seul `/way`.
- Compagnon, 12/12 : « Rends tes 13 quêtes terminées avant tout : ton journal est plein »,
  avec les PNJ et les `/way`.

**C10 — « Les Éolides, c'est quelles classes ? » : un cas où le généraliste fait aussi bien**
- ChatGPT (A et B), 11/12 : classes par faction, île de Zéphras, niveaux 1 à 12, pack requis.
  Juste et sourcé.
- Compagnon, 12/12 : même contenu, plus court.

## Limites (à afficher avec les résultats)

- **Références et compagnon partagent leurs sources.** Les références vérifiées ont été
  rédigées à partir de QuestieDB, de la base du client et des connaissances Forever du
  compagnon. Le compagnon y colle donc presque mot pour mot (C03 : mêmes `/way`). Un
  concurrent dont la source diffère (autre point d'apparition, article plus récent) perd des
  points même s'il n'a pas tort. Le 11,8 du compagnon est surestimé par ce biais ; l'écart sur
  les questions liées au perso, lui, ne dépend pas de la référence.
- **Juges de la même famille.** Le compagnon tourne sur Claude, les juges aussi (Sonnet,
  modèle différent). Le protocole recommande un second juge humain ou d'un autre fournisseur.
- **ChatGPT a vu l'historique du compte** malgré le chat éphémère : il savait que le joueur
  est un chasseur nain aux Paluns. Ce biais l'avantage en condition A.
- **C01 et C02 de ChatGPT (A)** ont été posés par le joueur lui-même ; en C01, ChatGPT a d'abord
  demandé des précisions. Seule sa première réponse a été notée.
- **Ce que la note ne mesure pas** : la vitesse et les visuels. ChatGPT répond en 10 à 20 s et
  insère des cartes ; Gemini insère des vidéos. Voir `observations.md`.
- Un seul tirage par question, offres gratuites, le 18/11/2026. Les réponses changent d'un jour
  à l'autre.
