---
name: forever-profil
description: Persos et notes du joueur WoW Forever (perso/<Utilisateur>/<Perso>-<Région>/) : changer de perso actif, rattacher un compte à un prénom, noter un objectif, régler la voix, créer un profil à la main sans addon. À utiliser pour « je joue mon mage », « note que… », « mon objectif est… », « qui sont mes persos ? », ou quand aucun perso n'est trouvé. EN: The player's WoW Forever characters and notes: switch character, link an account, note a goal, set the voice, create a profile by hand. Use for "I'm playing my mage", "note that…", "who are my characters?".
---

# Profil, persos et notes

```
perso/
├── config.json      dossier du jeu, comptes → prénoms, perso actif, voix, langue
└── <Utilisateur>/<Perso>-<Région>/
    ├── profil.md    section auto (addon) + notes du joueur
    ├── objectifs.md rédigé avec le joueur
    ├── journal.md   « Mes notes » (joueur) + « Journal automatique » (synchro)
    ├── etat.json    dernière capture ; resume.json (résumé calculé)
    └── historique/  un instantané par jour
```

> Réponds dans la langue de la question et passe `lang` (`fr`/`en`) ; les noms du jeu restent ceux du client. Forme et voix : instructions du serveur `forever` (verdict en gras d'abord, badge de source).

## Appels (budget : 1 outil)

- « Qui sont mes persos ? » → `characters`.
- « Je joue mon mage » → `characters action:activer perso:<nom>`.
- Compte affiché « Compte-<id> » → demander à qui il appartient, puis
  `characters action:rattacher account:<id> user:<prénom>`.
- Comparer deux persos → `characters action:comparer persos:[…]`.
- Perso « jamais capturé » → le connecter en jeu avec ForeverScribe, puis Ctrl+Maj+S.
- Voix des réponses → `"voix": "joueur" | "pnj" | "neutre"` dans `config.json` (`voix.md`).

## Notes du joueur

- Ne jamais écrire entre `<!-- auto:debut -->` et `<!-- auto:fin -->` ni dans le « Journal
  automatique ».
- Objectif, décision, plan → une ligne datée `- AAAA-MM-JJ : …` en haut de « Mes notes » de
  `journal.md`, ou `objectifs.md`. Montrer la ligne au joueur et attendre son accord.

## Sans addon

1. Proposer d'installer ForeverScribe (`addon/install.sh` ou `install.ps1`).
2. Sinon créer `perso/<Prénom>/<Perso>-<Région>/` à partir de `perso.example/`, demander en un
   message race, classe, niveau, faction, ruleset, zone, métiers, objectifs ; `inconnu` pour
   ce qui manque.
