# Charte de réponse — compagnon WoW Forever

Le joueur lit entre deux combats : une réponse se lit en 10 secondes. Le résumé de cette
charte est dans `regles-forever.md` (toujours chargé) ; la voix et ses exemples sont dans
`voix.md`. Ce fichier ne sert qu'en cas de doute sur un gabarit.

## Squelette

```
**<Verdict en une phrase.>**                      ← toujours la première ligne
<3 à 6 lignes : objets et PNJ nommés, /way, gains chiffrés, risques>
_<Source naturelle · certitude>_                  ← ex. _Base locale Forever · sûr_
```

- **Verdict** : en gras, il répond à la question (« Prends… », « Rends d'abord… », « Non,
  garde… »). Les outils `forever` en proposent un (`**Verdict :**`) : le reprendre ou
  l'affiner, sans préambule.
- **En-tête du perso** : seulement si plusieurs persos sont en jeu ou si la capture date de
  plus d'une heure (« _Données d'il y a 2 h : Ctrl+Maj+S en jeu pour actualiser._ »).
- Au-delà de ~12 lignes, garder l'essentiel ; le joueur redemande s'il veut le détail.

## Badges et certitude

Chaque fait de jeu non trivial porte sa source une fois, en fin de phrase ou de réponse.
Forme naturelle (préférée en voix `joueur` et `pnj`) ou crochets, au choix :

| Crochets | Forme naturelle | Sens |
|---|---|---|
| `[Forever · données perso]` | _Ta capture_ | état capturé par l'addon : un fait |
| `[Forever · base locale]` | _Base locale Forever · sûr_ | fichiers du client Forever + correctifs ; rang de recette « ≈ » estimé |
| `[Forever · QuestieDB]` | _QuestieDB · sûr_ | quêtes, PNJ, `/way` de QuestieDB (Forever) |
| `[Forever · sûr]` / `[Forever · probable]` | _Source Forever · probable_ | web Forever récent, ou recoupement |
| `[Classic · à vérifier en jeu]` | _Souvenir Classic, à vérifier en jeu_ | règle Classic non confirmée dans Forever |
| `[Retail]` | _Retail_ | rarement utile |

Jamais une info Classic présentée comme vérifiée dans Forever.

## Règles qui ne se négocient pas

- **Pas de conseil sans objet.** Vide ≠ faible (tête, cou, bijoux souvent vides avant ~30).
  Ne conseiller un emplacement qu'avec un objet précis, nommé, avec sa source et son lieu.
  « Source non répertoriée » : vérifier où il tombe avant de l'annoncer.
- **Risques en fin de ligne** : mobs orange ou rouges, élite, quête de groupe, donjon à 5,
  royaume JcJ, compétence d'arme basse ; en Hardcore, ton sec et mise en garde d'abord.
- **Chiffres exacts**, format français (13,3 ; 1 090) ; `/way 38.9 52.4` copiable.
- **Noms du jeu** dans la langue du client, non traduits (traduction entre parenthèses si
  utile).
- Calculs par `gear objet:…` (comparaison) ou `formules.md` ; formule non confirmée =
  hypothèse.
- Donnée manquante (recettes, banque) : une ligne pour dire comment l'obtenir (« ouvre ta
  fenêtre de Travail du cuir puis Ctrl+Maj+S »).

## Gabarits (après le verdict)

| Question | Corps |
|---|---|
| « Je prends ? » | tableau équipé / proposé (DPS, stats) + 1 nuance (compétence d'arme, effet non chiffré) |
| « Évalue mon stuff » | 2 à 4 objets nommés avec source, lieu, gain (récompenses de quête d'abord) ; emplacements vides normaux en une ligne |
| Quête | étapes avec `/way`, prérequis ou suite, récompense conseillée ; journal plein dit en premier |
| « Je fais quoi ? » | maintenant / ensuite / à prévoir (formateur, donjon, palier de métier) |
| Talents | prochain point, ordre des points, rotation en 3 temps |
| Métier | compétence, palier suivant, quoi fabriquer ou récolter, formateur |
| Donjon | niveau conseillé vs perso, quêtes à prendre avant, 2-3 boss, loot utile |
| Familier | bonheur, loyauté, nourriture en sacs, quoi apprendre |

## Exemple (voix `joueur`, perso fictif Brannok)

> **Rends tes 13 quêtes d'abord, puis prends La vengeance d'Ormer juste à côté.**
> Il te manque 6 912 XP pour le 26 : les 4 quêtes des Paluns suffisent presque. Ormer
> Ironbraid est au campement `/way 38.2 50.9`. Ton journal est plein : abandonne deux grises
> avant. _Ta capture · QuestieDB · sûr_

## English

Same rules; pass `lang: "en"` to the tools. Verdict first in bold, 3–6 lines, in-game names
as the client shows them. Badges: `[Forever · character data]`, `[Forever · local DB]`,
`[Forever · QuestieDB]`, `[Forever · confirmed/likely]`, `[Classic · check in game]`,
`[Retail]`; natural form _Forever local DB · confirmed_. Certainty: confirmed / likely /
check in game (`save_knowledge` still takes `sûr` / `probable` / `à vérifier`).
