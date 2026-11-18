// Site de présentation. ui-kit (bibliothèque privée de l'auteur) est lu depuis un dossier voisin :
// variable UIKIT, sinon ../../ui-kit (le dépôt ui-kit cloné à côté de wow-forever-companion).
// Aucun code ui-kit n'est copié dans ce dépôt ; seul le build (site/dist) l'embarque.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { existsSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const UIKIT = resolve(process.env.UIKIT ?? resolve(here, "../../ui-kit"));
if (!existsSync(resolve(UIKIT, "src/index.ts"))) {
  throw new Error(`ui-kit introuvable dans ${UIKIT}. Clone-le à côté du dépôt ou indique UIKIT=/chemin/vers/ui-kit.`);
}

// Captures en jeu fournies par le mainteneur (public/captures/) : la section ne s'affiche que si elles existent.
const capDir = resolve(here, "public/captures");
const CAPTURES = existsSync(capDir) ? readdirSync(capDir).filter((f) => /\.(png|jpe?g|webp)$/i.test(f)).sort() : [];

export default defineConfig({
  define: { __CAPTURES__: JSON.stringify(CAPTURES) },
  // GitHub Pages sert le site sous /wow-forever-companion/ ; BASE=/ pour un domaine propre.
  base: process.env.BASE ?? "/wow-forever-companion/",
  plugins: [react()],
  resolve: {
    alias: [
      { find: "@ui-kit/styles", replacement: resolve(UIKIT, "styles") },
      { find: "@ui-kit", replacement: resolve(UIKIT, "src/index.ts") },
    ],
    dedupe: ["react", "react-dom"],
  },
  server: { port: 5193, strictPort: true, fs: { allow: [here, UIKIT] } },
  preview: { port: 5194, strictPort: true },
  build: { target: "es2020", cssMinify: true },
});
