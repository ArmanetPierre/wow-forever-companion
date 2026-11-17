---
name: forever-profil
description: Gère les personnages et les notes du joueur WoW Forever (perso/<Utilisateur>/<Perso>-<Région>/ : profil.md, objectifs.md, journal.md) : changer de perso actif, rattacher un compte à un prénom, noter un objectif ou une décision, créer un profil à la main quand l'addon n'est pas installé. À utiliser pour « je joue mon mage », « note que… », « mon objectif est… », « qui sont mes persos ? », « crée mon perso », ou quand aucun perso n'est trouvé.
---

# Profil, persos et notes

Organisation (dossier personnel, jamais partagé) :

```
perso/
├── config.json                    dossier du jeu, comptes → prénoms, perso actif
└── <Utilisateur>/<Perso>-<Région>/
    ├── profil.md       section auto (addon) + notes du joueur
    ├── objectifs.md    rédigé avec le joueur
    ├── journal.md      « Mes notes » (joueur) + « Journal automatique » (synchro)
    ├── etat.json       dernière capture
    └── historique/     un instantané par jour
```

## Persos et comptes (outils MCP `forever`)

- « Qui sont mes persos ? » → `list_characters`.
- « Je joue mon mage » → `set_active_character` avec son nom.
- Un compte affiché « Compte-<id> » → demande à qui il appartient, puis `register_account`.
- Un perso « jamais capturé » → le connecter en jeu avec ForeverScribe actif, puis
  Ctrl+Maj+S (ou `/sync`).

## Notes du joueur

- Les sections entre `<!-- auto:debut -->` et `<!-- auto:fin -->`, et le « Journal
  automatique », sont réécrits par la synchro : **ne jamais y écrire**.
- Objectif, décision, ressenti, plan → une ligne datée `- AAAA-MM-JJ : …` en haut de
  « Mes notes » dans `journal.md`, ou une mise à jour de `objectifs.md`. Toujours avec
  l'accord du joueur, en lui montrant la ligne avant de l'écrire.
- `objectifs.md` : objectif principal, objectifs secondaires, style de jeu, contraintes
  (temps de jeu, amis, ruleset). Pose les questions en un seul message court.

## Sans addon (création à la main)

Si l'addon n'est pas installé ou qu'aucun perso n'est trouvé :
1. Propose d'abord d'installer ForeverScribe (`addon/` du repo, script `install.sh` ou
   `install.ps1`) : le profil se remplira seul.
2. Sinon, crée `perso/<Prénom>/<Perso>-<Région>/` à partir de `perso.example/Personnage/`
   s'il existe, demande en un message : race, classe, spé, niveau, faction, ruleset, zone,
   métiers et niveaux, objectifs. Mets `inconnu` pour ce qui manque et `(à confirmer)` après
   une valeur déduite.
