# Contribuer

Merci de ton aide ! Quelques règles simples :

1. **Aucune donnée de joueur** dans une contribution : pas de fichier SavedVariables réel,
   numéro de compte, GUID, nom de perso réel ni chemin personnel. Utilise le perso
   fictif Brannok et les fixtures de `addon/tests/fixtures/`.
2. **Lance les tests** (voir `CLAUDE.md`) : addon, parseur/synchro, serveur de bout en
   bout, `claude plugin validate .`.
3. **Format de données** : toute nouvelle donnée capturée est décrite dans
   `docs/schema.md`.
4. **API du jeu** : si tu découvres ce qu'une fonction renvoie dans Forever, complète
   `docs/api-inventaire.md`. L'addon `ForeverProbe` aide à le vérifier en jeu
   (voir son `LISEZMOI.md`).
5. **Connaissances** : un fait ajouté à `knowledge/` a une source (lien) et un niveau de
   certitude. Pas de source, pas de fait.
6. Python : bibliothèque standard uniquement. Lua : compatible 5.1 (client WoW).

Ouvre une issue pour discuter d'un changement important avant de le coder.
