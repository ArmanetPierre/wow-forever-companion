# Pré-vérifications (à ne PAS donner au juge)

Repères notés à la réception des réponses, vérifiés dans la base locale (QuestieDB +
client Forever) et `knowledge/donjons.json`. Le juge note à l'aveugle ; ces notes servent
ensuite à contrôler sa note et à choisir les exemples.

## C01 — ChatGPT, prompt A (18/11/2026)

**Ce qui est juste**
- Le donjon Forever *Excavations : les Paluns* (Excavation Site: Wetlands), niveau 24-29 :
  conforme à notre base (réponse 1).
- *Uncovering the Past* (Découverte du passé) chez Whelgar, *Blisters on the Land*,
  *Apprentice's Duties*, *The Eye of Paleth* → Benedictus : quêtes réelles des Paluns.
- Conseil prudent sur les élites.

**Ce qui est faux ou invérifiable**
- Le donjon passe à « 26-31 » dans la réponse 2 : la réponse se contredit (base : 24-29).
- *Ormer's Revenge* : « 10 Mottled Scytheclaw et 10 Mottled Razormaw ». La base dit
  10 Hurleurs tachetés et 10 Raptors tachetés.
- *Return the Statuette* : donnée par « Captain Stoutfist » dans le tableau, alors que
  l'étape A dit Karl Boran. La quête part d'un objet (Tonneau à moitié enseveli,
  `/way 13.9 34.8`) et se rend à Karl Boran (`/way 8.3 58.6`).
- *Crocs of the Sky*, *Carnage*, *Razormaw Needling*, *Trying Times*, *Death to the
  Dragonmaw* (PNJ « Howin Kindfeather ») : introuvables dans QuestieDB, dans le client et sur
  Wowhead. Probablement inventées. Forever ajoute des quêtes : à confirmer en jeu avant de
  l'affirmer publiquement.
- « Hautes-terres Arathies : nouvelle zone Alliance » : faux, la zone existe depuis Classic.
- « Détournement : garde Feindre la mort » : mélange de deux sorts. Détournement
  (Misdirection) n'existe pas au niveau 25 en Classic.
- Aucun `/way`, aucune coordonnée.
- Bois de la Pénombre conseillé à 26-28 puis à 30-32 dans la même conversation.

**Ce qui manque (prompt A sans données, donc attendu)**
- Ignore le journal plein et les 13 quêtes à rendre (il ne peut pas les connaître).
- Ne mentionne pas le maître de classe au niveau 26.
- A demandé des précisions avant de répondre : le joueur a dû faire un second message.

**Exemple vitrine possible** : « ChatGPT : 7 étapes, dont 5 quêtes introuvables dans les
données du jeu. Le compagnon : rends tes 13 quêtes d'abord, voici où, avec `/way`. »

## C02 — ChatGPT, prompt A (18/11/2026)

**Ce qui est juste** (bonne réponse, à garder comme cas où ChatGPT s'en sort)
- Les statistiques des deux armes sont exactes : 24-37, vitesse 2,0, 15,2 DPS, +12 PA à
  distance, niveau 26 contre 21-40, vitesse 2,3, 13,3 DPS, +3 For et +3 Agi, niveau 22. Il
  les a trouvées sur le web (source « [Forever] »).
- Il voit le niveau 26 requis : « garde ton fusil jusqu'au 26 ».
- Il ne tombe pas dans le piège du bonus racial nain aux fusils.

**Ce qui est imprécis ou manquant**
- « Environ 15 % de DPS supplémentaire » : c'est le gain du DPS de l'arme seule
  (13,3 → 15,2). Le gain réel à distance, puissance d'attaque comprise, est d'environ +5,6 %
  (≈ +2,4 DPS). Le gain est donc surestimé à peu près trois fois.
- Il ne parle pas de la compétence Arbalètes : un nain chasseur ne l'a pas de base, il faut
  l'apprendre chez un maître d'armes, puis la monter (1/125 chez Brannok). C'est le vrai frein.
- Il oublie les +3 Force perdus. C'est sans effet à distance, donc ce n'est pas grave.

## Premier survol des 46 autres réponses (18/11/2026, avant le juge)

À confirmer par le juge et la base locale ; repères seulement.

**Erreurs marquantes, candidates pour la vitrine**
- Gemini A03 : présente WoW Forever comme un « serveur privé » sur « l'extension WotLK 3.3.5 »,
  et conseille de vider le dossier Cache. C'est faux : Forever est un produit officiel Blizzard.
- Gemini A04 : confond points de dressage du familier et points de talent du chasseur. Il
  donne un arbre Maîtrise des bêtes avec des talents mal nommés (« Endurance d'endurance »).
- Gemini A02 : « mets des carreaux, pas des balles ». Les carreaux n'existent pas en Classic :
  les arbalètes tirent des flèches. En revanche, les niveaux d'objet 27 et 31 sont exacts.
- Gemini B01 : propose de se débarrasser des ingrédients du Goulash. Il cite un « Fort de
  Dun Algaz » pour rendre les quêtes et écrit « loyheur ».
- Gemini B06 : donne le donjon des Paluns pour les niveaux 26-33 (la base dit 24-29).
  ChatGPT A01 donne 26-31.
- ChatGPT A05 et B05 : les dates des correctifs changent d'une conversation à l'autre
  (8 octobre, 9 novembre, 14 novembre contre 8 novembre, 10 novembre, 13 novembre, avec un
  seuil de 12 ou de 13 niveaux).
- ChatGPT A01 : 5 quêtes introuvables (voir C01 plus haut).

**Là où les généralistes s'en sortent (à montrer aussi)**
- GDKP (C08) : les deux répondent juste, sources datées, nuance des régions NA/EU.
- Rulesets (C09) : les deux disent non pour les donjons.
- Raids du 9/12 (C07) et Onyxia par perso (C12) : globalement justes chez les deux.
- Éolides (C10) : les deux donnent les classes par faction et l'île de Zéphras.
- C02 en B : les deux voient le niveau 26 et la compétence à 1/125.

**Biais du protocole**
- ChatGPT a utilisé l'historique du compte même en chat éphémère (Paluns, nain, Alliance).
  Ce biais l'avantage en condition A.
