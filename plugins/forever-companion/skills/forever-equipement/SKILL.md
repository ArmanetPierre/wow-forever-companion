---
name: forever-equipement
description: Équipement dans WoW Forever : comparer un objet à celui porté (« je prends ? »), améliorations à portée, récompense de quête à choisir, quoi garder ou vendre, sacs pleins, munitions. À utiliser dès que le joueur cite un objet, un loot, une récompense, ses sacs ou demande comment s'améliorer. EN: WoW Forever gear: compare an item with the worn one, reachable upgrades, quest reward choice, keep or sell, full bags, ammo. Use whenever the player mentions an item, loot, reward or bags.
---

# Équipement

> Réponds dans la langue de la question et passe `lang` (`fr`/`en`) ; les noms du jeu restent ceux du client. Forme et voix : instructions du serveur `forever` (verdict en gras d'abord, badge de source).

## Appels (budget : 1 outil, 2 au plus ; web seulement si rien n'est trouvé)

- « Évalue mon stuff », « comment m'améliorer ? » → `gear` (un emplacement : `emplacement`).
  Il classe en un appel les récompenses des quêtes du journal, les objets déjà dans les sacs
  et la base locale (source connue d'abord).
- « Je prends ? » → `gear` avec `objet` (nom ou id) ou `stats` (stats données par le joueur) :
  gain en DPS effectif, alertes (compétence d'arme, stats perdues).
- Fiche d'un objet cité → `item`. Sacs pleins, quoi vendre → `bags`.
- Rien d'utile → `search`, puis 2 ou 3 appels web (`site:wowhead.com/forever <emplacement>
  <niveau>`), puis `save_knowledge`.

Calculs : `formules.md` (14 PA = 1 DPS confirmé). Crit et effets « Chance quand vous
touchez » ne sont pas chiffrés : les mentionner.

## Règles

- Vide ≠ faible : pas de conseil d'emplacement sans objet précis à ce niveau.
- Chaque objet conseillé est nommé avec sa source et son lieu ; « source non répertoriée » :
  vérifier où il tombe avant de l'annoncer.
- Risques : mobs plus hauts, groupe, JcJ, compétence d'arme basse.
