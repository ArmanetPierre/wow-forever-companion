# Formules de calcul — WoW Forever

> Pour comparer un objet, utilise d'abord l'outil MCP `gear` avec `objet` ou `stats` : il applique ces
> formules avec les vraies stats du perso. Ce fichier sert à expliquer un calcul ou à
> estimer ce que l'outil ne couvre pas.
>
> Certitude : **sûr** = vu dans Forever (infobulle, capture de l'addon) · **probable** =
> cohérent avec les données réelles mais vérifié sur un seul cas · **à vérifier** = règle
> de Classic non confirmée dans Forever.

## DPS d'une arme `[Forever · sûr]`

```
DPS arme = (dégâts min + dégâts max) / 2 / vitesse
```
Le jeu l'affiche dans l'infobulle ; l'addon le capture (`get_equipment`).

## Puissance d'attaque → DPS `[Forever · sûr]`

```
DPS ajouté = PA / 14
```
Confirmé par l'infobulle de la fiche de personnage de Forever (17/11/2026) : « Chaque tranche
de 14 points de puissance d'attaque à distance ajoute 1 point de dégâts par seconde ».
Vaut pour la mêlée aussi en Classic `[Classic · à vérifier]`.

Dégâts d'un coup blanc ≈ dégâts de l'arme + (PA / 14) × vitesse de l'arme.

## Caractéristiques → puissance d'attaque

| Classe | PA à distance | PA en mêlée | Certitude |
|---|---|---|---|
| **Chasseur** | 2 par point d'Agi | 1 par point d'Agi + 1 par point de For | `[Forever · probable]` : retrouvé exactement sur les stats réelles de Brannok niveau 25 (PA distance 193 = 47 + 2 × 73 Agi ; PA mêlée 168 = 47 + 48 For + 73 Agi) |
| Voleur | 1 par point d'Agi | 1 par point d'Agi + 1 par point de For | `[Classic · à vérifier]` |
| Guerrier, Paladin, Chaman | 1 par point d'Agi (armes à distance des guerriers) | 2 par point de For | `[Classic · à vérifier]` |
| Druide | — | 2 par point de For (+ Agi en forme de félin) | `[Classic · à vérifier]` |
| Mage, Prêtre, Démoniste | — | 1 par point de For | `[Classic · à vérifier]` |

Source Classic : [warcraft.wiki.gg – Attack power](https://warcraft.wiki.gg/wiki/Attack_power).

## Agilité → coup critique `[Classic · à vérifier]`

Au niveau 60 en Classic, un chasseur gagne environ **1 % de crit pour 53 points d'Agi**. La
valeur dépend du niveau (moins de points nécessaires à bas niveau). Pas de valeur Forever
trouvée : ne pas chiffrer le crit dans une comparaison, le mentionner comme bonus non chiffré.
Sources : [Icy Veins – Classic Hunter stat priority](https://www.icy-veins.com/wow-classic/hunter-dps-pve-stat-priority), [warcraft.wiki.gg – Critical strike](https://warcraft.wiki.gg/wiki/Critical_strike).

## Compétence d'arme et ratés

- **Les compétences d'armes existent dans Forever** `[Forever · sûr]` : la capture de Brannok
  montre Armes à feu 124/125 et Arbalètes 1/125. Le plafond est 5 × le niveau du perso.
  Changer de type d'arme demande de monter la nouvelle compétence en l'utilisant.
- **Effet sur les ratés** `[Classic · à vérifier]` : la défense d'un monstre vaut 5 × son
  niveau. À compétence égale, environ 5 % de ratés contre un monstre de ton niveau ; chaque
  point de compétence en dessous de sa défense augmente les ratés. Avec une compétence très
  basse (1/125), la majorité des coups ratent au début.
  Source : [Wowhead – Classic hunter stat priority](https://www.wowhead.com/classic/guides/hunter-dps-stat-priority-classic-wow).
- Le bonus racial de compétence (ex. nains et armes à feu) **n'existe plus** dans Forever
  `[Forever · probable]` : [Warcraft Tavern – Weapon Skills in Forever](https://www.warcrafttavern.com/forever/news/weapon-skills-in-world-of-warcraft-forever/).

## Expérience et repos

- XP restante pour le niveau suivant : `get_character` la donne directement
  (`XP max − XP actuelle`).
- **Repos** `[Retail · à vérifier dans Forever]` : à l'auberge ou en capitale, environ 5 %
  d'un niveau par 8 h hors ligne, quatre fois moins ailleurs ; plafond 150 % d'un niveau.
  L'XP des monstres tués est doublée tant qu'il reste du repos (les quêtes ne consomment pas
  le repos). Source : [warcraft.wiki.gg – Rest](https://warcraft.wiki.gg/wiki/Rest).
  L'addon capture le repos disponible (`get_character`, ligne XP).

## XP d'une quête `[Classic · estimation]`

**Priorité à l'XP capturée** `[Forever · sûr]` : quand l'addon a lu la récompense d'une quête
du journal (`rewards.xp`), c'est la valeur exacte pour ce perso, déjà réduite selon son niveau ;
elle remplace l'estimation (les outils l'affichent sans « ≈ »). L'estimation ne sert que pour
les quêtes non encore ouvertes en jeu (quêtes d'une zone, de la base QuestieDB).

```
XP estimée = XP pleine(niveau de la quête) × facteur(niveau du perso − niveau de la quête)
```

- **XP pleine** (`quest_base_xp` dans `mcp/xptable.py`) : interpolation linéaire entre des
  repères par niveau de quête, arrondie (multiple de 5, 10, 25 ou 50 selon la taille) :

  | Niveau | 1 | 5 | 9 | 10 | 12 | 20 | 30 | 40 | 50 | 60 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | XP pleine | 100 | 420 | 775 | 850 | 1 150 | 1 800 | 2 900 | 3 950 | 5 000 | 6 600 |

  Les niveaux 9, 10 et 12 sont calés sur des récompenses relevées dans Forever ; le reste suit
  les ordres de grandeur de Classic Era.
- **Facteur** (`quest_xp_factor`, règle de Classic, cmangos `Quest::XPValue`) :

  | Perso au-dessus de la quête | ≤ +5 | +6 | +7 | +8 | +9 | ≥ +10 |
  |---|---|---|---|---|---|---|
  | Part de l'XP pleine | 100 % | 80 % | 60 % | 40 % | 20 % | 10 % |

- Au niveau maximum (60), une quête ne rapporte plus d'XP (`quest_xp` renvoie 0).
- **Marge : environ ±30 %.** La vraie valeur dépend de la difficulté propre de chaque quête,
  absente de la base locale (escortes, messagers et quêtes d'élite s'écartent le plus). Toujours
  présenter le chiffre comme « ≈ » et ne pas en tirer de conclusion au point près.
- Totaux d'XP (rendus, journal entier) : somme des XP capturées quand elles existent, sinon des
  estimations, puis niveau atteint avec la table d'XP par niveau du client Forever (`xp_levels`,
  repli Classic Era).

## Comparer deux objets (méthode)

1. Prendre les stats de l'objet équipé (`get_equipment`) et du nouvel objet.
2. Convertir Agi/For en PA avec le tableau ci-dessus, puis PA en DPS (÷ 14).
3. Ajouter la différence de DPS de l'arme si c'est une arme.
4. Signaler sans chiffrer : crit, endurance (survie), effets « Chance quand vous touchez »,
   compétence d'arme à monter, bonus d'ensemble.
