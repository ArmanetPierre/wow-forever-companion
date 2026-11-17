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
