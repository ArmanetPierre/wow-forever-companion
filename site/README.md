# Site de présentation

Page unique (Vite + React + TypeScript), FR/EN, publiée sous `/wow-forever-companion/`.

Il importe le **ui-kit** (FlowDiagram, SegmentedControl, Stepper) depuis un dossier voisin,
sans le copier : par défaut `../../ui-kit`, ou le chemin donné par la variable `UIKIT`.

```bash
cd site
npm install
npm run dev        # http://localhost:5193/wow-forever-companion/
npm run build      # site/dist
npm run preview    # http://localhost:5194/wow-forever-companion/
```

`BASE=/autre-chemin/ npm run build` change le sous-chemin. Les textes sont dans
`src/content.ts`, les schémas dans `src/diagrams.ts`, la direction artistique dans
`src/styles.css`. Les captures de référence sont dans `screenshots/`.

Aucun élément graphique de Blizzard : polices Google, ornements et carte dessinés pour ce site.
