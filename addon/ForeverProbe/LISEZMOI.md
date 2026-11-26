# ForeverProbe — sonde de l'API

Addon temporaire : il liste ce que l'API de WoW Forever permet vraiment de lire.
Il ne modifie rien dans le jeu. On le supprimera une fois ForeverScribe construit.

## Utilisation

1. **Lance le jeu**, ou fais `/reload` si tu es déjà connecté.
2. À l'écran de sélection des personnages, bouton **AddOns** : vérifie que
   **ForeverProbe** est coché. S'il est marqué « obsolète », coche
   **Charger les addons obsolètes**.
3. Connecte-toi avec Brannok. **Appelle ton familier** si possible (pour tester son API).
4. Après 5 secondes, la sonde se lance seule. Le message apparaît dans le chat :
   `Sonde terminée : X fonctions trouvées, Y tests OK, Z erreurs…`
   Tu peux la relancer à tout moment avec `/probe`.
5. Optionnel mais utile : ouvre ta **fenêtre de métier** et ta **banque**, puis `/probe` à nouveau.
6. Tape **`/reload`** : c'est ce qui écrit le fichier sur le disque.
7. Préviens Claude. Le fichier produit est :

```
/Applications/World of Warcraft/_forever_/WTF/Account/123456789#1/SavedVariables/ForeverProbe.lua
```

## Hôtel des ventes : `/probe hv`

Sert à vérifier quelle API d'hôtel des ventes (HV) a Forever avant de se fier aux prix
relevés par ForeverScribe 1.5.

1. Va voir un commissaire-priseur, **hors combat**.
2. Tape **`/probe hv`** (ou `/fprobe hv`). Le chat affiche :
   - le nombre de fonctions `C_AuctionHouse` (API moderne) et les fonctions classiques
     présentes (`GetNumAuctionItems`, `GetAuctionItemInfo`…) ;
   - les événements d'HV acceptés par le client, puis ceux qu'il refuse.
3. Ouvre l'HV et **fais toi-même une recherche** (ex. « cuir »), clique sur un objet,
   change de page. Pour chaque événement reçu, une ligne s'affiche, par exemple :
   `HV AUCTION_ITEM_LIST_UPDATE : n=50 · page 0 · #1 Cuir léger x5 buyout=125 id=2318`
   ou `HV COMMODITY_SEARCH_RESULTS_UPDATED : n=4 · #1 id=4234 price=230`.
   `n` = nombre de résultats, `buyout` / `price` = prix d'achat immédiat (en pièces de
   cuivre), `id` = itemId.
4. `/probe hv stop` pour arrêter, puis **`/reload`** pour écrire le fichier.
   Le détail (3 premières lignes de chaque résultat, 40 derniers événements) est dans
   `ForeverProbeDB.auction` (`inventaire`, `log`).

La sonde **ne lance aucune recherche** : `QueryAuctionItems` et
`C_AuctionHouse.Send*Query` sont seulement signalés comme présents, jamais appelés. Les
noms des vendeurs et enchérisseurs sont masqués. Rien n'est lu en combat.

Ce qu'il faut rapporter à Claude : la ligne « Hôtel des ventes : … », la liste des
événements connus, et une ou deux lignes reçues pendant ta recherche (avec ou sans
`id=` et `buyout=`/`price=` remplis).

## Installation

Déjà faite sur ce Mac : un lien symbolique relie
`Interface/AddOns/ForeverProbe` à ce dossier du projet.

Si le jeu ne voit pas l'addon (lien symbolique ignoré), copie plutôt le dossier :

```bash
rm "/Applications/World of Warcraft/_forever_/Interface/AddOns/ForeverProbe"
cp -R <repo>/addon/ForeverProbe "/Applications/World of Warcraft/_forever_/Interface/AddOns/"
```

## Données enregistrées

Noms des fonctions disponibles et échantillons de retour (ton perso, ton équipement,
tes quêtes). Le BattleTag n'est **pas** enregistré : seulement le fait qu'il soit lisible.

## Désactiver la sonde

Une fois ForeverScribe validé, la sonde n'est plus utile :
- en jeu : écran de sélection des personnages → **AddOns** → décoche **ForeverProbe** ;
- ou supprime le lien (le dossier du repo n'est pas touché) :
  `rm "/Applications/World of Warcraft/_forever_/Interface/AddOns/ForeverProbe"`
