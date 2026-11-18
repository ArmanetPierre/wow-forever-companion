// Schémas interactifs (FlowDiagram d'ui-kit), mêmes faits que docs/marketing/schemas, en FR et en EN.
import type { FlowDiagramDef, FlowScenario } from "@ui-kit";
import { typoEn, typoFr, type Lang } from "./content";

type T = { fr: string; en: string };
const t = (lang: Lang, x: T) => (lang === "fr" ? typoFr(x.fr) : typoEn(x.en));

/* 1. Comment il répond --------------------------------------------------------------------------- */
const D = { y: 150, h: 64, c: 182 };
const S = { y: 34, h: 60 };

export function answerDiagram(lang: Lang): FlowDiagramDef {
  const L = (fr: string, en: string) => t(lang, { fr, en });
  return {
    width: 1200,
    height: 370,
    zones: [
      { label: L("1 · ton perso", "1 · your character"), x: 150, w: 180 },
      { label: L("2 · données du jeu", "2 · game data"), x: 350, w: 180 },
      { label: L("3 · règles Forever", "3 · Forever rules"), x: 550, w: 180 },
      { label: L("4 · il manque un bout ?", "4 · anything missing?"), x: 750, w: 185 },
      { label: L("réponse", "answer"), x: 945, w: 255 },
    ],
    nodes: [
      { id: "q", label: L("Ta question", "Your question"), sublabel: L("FR ou EN", "EN or FR"), kind: "step", x: 0, y: D.y, w: 120, h: D.h },
      { id: "d1", label: L("Ça dépend de ton perso ?", "Depends on your character?"), kind: "decision", x: 170, y: D.y, w: 140, h: D.h },
      { id: "s1", label: L("Ton perso", "Your character"), sublabel: "addon ForeverScribe", kind: "store", x: 170, y: S.y, w: 140, h: S.h },
      { id: "d2", label: L("Une donnée du jeu ?", "Game data?"), sublabel: L("objet, quête, PNJ", "item, quest, NPC"), kind: "decision", x: 370, y: D.y, w: 140, h: D.h },
      { id: "s2", label: L("Base du jeu", "Game database"), sublabel: "client + QuestieDB", kind: "store", x: 370, y: S.y, w: 140, h: S.h },
      { id: "d3", label: L("Une règle Forever ?", "A Forever rule?"), sublabel: L("raids, XP, GDKP…", "raids, XP, GDKP…"), kind: "decision", x: 570, y: D.y, w: 140, h: D.h },
      { id: "s3", label: L("Connaissances", "Knowledge"), sublabel: L("sourcées et datées", "sourced and dated"), kind: "store", x: 570, y: S.y, w: 140, h: S.h },
      { id: "d4", label: L("Il manque une info ?", "Anything missing?"), kind: "decision", x: 770, y: D.y, w: 140, h: D.h },
      { id: "web", label: L("Wowhead ou web", "Wowhead or web"), sublabel: L("à la demande", "on demand"), kind: "step", x: 770, y: 290, w: 140, h: 60 },
      { id: "save", label: L("Il la garde", "It keeps it"), sublabel: L("cache local ou tes notes", "local cache or your notes"), kind: "store", x: 955, y: 290, w: 160, h: 60 },
      { id: "ans", label: L("Réponse", "Answer"), sublabel: L("verdict · /way · carte · source", "verdict · /way · map · source"), kind: "step", x: 975, y: D.y, w: 210, h: D.h },
    ],
    edges: [
      { id: "q-d1", from: "q", to: "d1", points: [[120, D.c], [170, D.c]] },
      { id: "d1-s1", from: "d1", to: "s1", label: L("oui", "yes"), labelAt: [240, 122], points: [[240, D.y], [240, S.y + S.h]] },
      { id: "s1-d2", from: "s1", to: "d2", points: [[310, 64], [340, 64], [340, 168], [370, 168]] },
      { id: "d1-d2", from: "d1", to: "d2", label: L("non", "no"), labelAt: [340, 214], points: [[310, 196], [370, 196]] },
      { id: "d2-s2", from: "d2", to: "s2", label: L("oui", "yes"), labelAt: [440, 122], points: [[440, D.y], [440, S.y + S.h]] },
      { id: "s2-d3", from: "s2", to: "d3", points: [[510, 64], [540, 64], [540, 168], [570, 168]] },
      { id: "d2-d3", from: "d2", to: "d3", label: L("non", "no"), labelAt: [540, 214], points: [[510, 196], [570, 196]] },
      { id: "d3-s3", from: "d3", to: "s3", label: L("oui", "yes"), labelAt: [640, 122], points: [[640, D.y], [640, S.y + S.h]] },
      { id: "s3-d4", from: "s3", to: "d4", points: [[710, 64], [740, 64], [740, 168], [770, 168]] },
      { id: "d3-d4", from: "d3", to: "d4", label: L("non", "no"), labelAt: [740, 214], points: [[710, 196], [770, 196]] },
      { id: "d4-ans", from: "d4", to: "ans", label: L("non", "no"), labelAt: [942, 168], points: [[910, D.c], [975, D.c]] },
      { id: "d4-web", from: "d4", to: "web", label: L("oui", "yes"), labelAt: [840, 252], points: [[840, D.y + D.h], [840, 290]] },
      { id: "web-save", from: "web", to: "save", points: [[910, 320], [955, 320]] },
      { id: "save-ans", from: "save", to: "ans", points: [[1035, 290], [1035, D.y + D.h]] },
    ],
  };
}

export const answerScenarios: Record<"quete" | "regle" | "nouveau", FlowScenario> = {
  quete: { route: ["q-d1", "d1-s1", "s1-d2", "d2-s2", "s2-d3", "d3-d4", "d4-ans"] },
  regle: { route: ["q-d1", "d1-d2", "d2-d3", "d3-s3", "s3-d4", "d4-ans"] },
  nouveau: { route: ["q-d1", "d1-d2", "d2-d3", "d3-d4", "d4-web", "web-save", "save-ans"] },
};

/* 2. Avec ou sans le serveur MCP -------------------------------------------------------------------- */
export function mcpDiagram(lang: Lang): FlowDiagramDef {
  const L = (fr: string, en: string) => t(lang, { fr, en });
  return {
    width: 1200,
    height: 410,
    zones: [
      { label: L("Question", "Question"), x: 0, w: 200 },
      { label: L("Ce qu'il consulte", "What it looks at"), x: 220, w: 690 },
      { label: L("Réponse (comparatif, sur 12)", "Answer (test, out of 12)"), x: 930, w: 270 },
    ],
    nodes: [
      { id: "q1", label: L("ChatGPT ou Gemini", "ChatGPT or Gemini"), sublabel: L("« je fais quoi ? »", "\"what now?\""), kind: "step", x: 20, y: 56, w: 160, h: 64 },
      { id: "mem", label: L("Mémoire du modèle + web", "Model memory + web"), sublabel: L("souvenirs de Classic, articles", "Classic memories, articles"), kind: "store", x: 380, y: 56, w: 330, h: 64 },
      { id: "r1", label: L("Réponse générale", "Generic answer"), sublabel: L("perso deviné ou recopié à la main ; questions perso : 3,0 à 7,8 /12 en moyenne", "character guessed or copied by hand; character questions: 3.0 to 7.8 /12 on average"), kind: "step", x: 950, y: 40, w: 230, h: 96 },
      { id: "q2", label: L("Compagnon", "Companion"), sublabel: L("« je fais quoi ? »", "\"what now?\""), kind: "step", x: 20, y: 264, w: 160, h: 64 },
      { id: "srv", label: L("Serveur forever", "forever server"), sublabel: L("MCP, sur ton PC", "MCP, on your PC"), kind: "step", x: 240, y: 264, w: 160, h: 64 },
      { id: "perso", label: L("Ton perso", "Your character"), sublabel: L("capture de l'addon", "addon capture"), kind: "store", x: 480, y: 196, w: 230, h: 50 },
      { id: "base", label: L("Base du jeu + cartes", "Game data + maps"), sublabel: L("fichiers du client, QuestieDB", "client files, QuestieDB"), kind: "store", x: 480, y: 271, w: 230, h: 50 },
      { id: "know", label: L("Règles de Forever", "Forever rules"), sublabel: L("sourcées, datées", "sourced, dated"), kind: "store", x: 480, y: 346, w: 230, h: 50 },
      { id: "r2", label: L("Réponse ancrée", "Grounded answer"), sublabel: L("12 sur 12 · 0 invention", "12 of 12 · nothing made up"), kind: "step", x: 950, y: 264, w: 230, h: 64 },
    ],
    edges: [
      { id: "q1-mem", from: "q1", to: "mem", label: L("aucun accès au jeu", "no access to the game"), labelAt: [280, 88], points: [[180, 88], [380, 88]] },
      { id: "mem-r1", from: "mem", to: "r1", points: [[710, 88], [950, 88]] },
      { id: "q2-srv", from: "q2", to: "srv", points: [[180, 296], [240, 296]] },
      { id: "srv-perso", from: "srv", to: "perso", points: [[400, 284], [440, 284], [440, 221], [480, 221]] },
      { id: "srv-base", from: "srv", to: "base", points: [[400, 296], [480, 296]] },
      { id: "srv-know", from: "srv", to: "know", points: [[400, 308], [440, 308], [440, 371], [480, 371]] },
      { id: "perso-r2", from: "perso", to: "r2", label: L("lecture locale : 0,1 à 0,3 s", "local read: 0.1 to 0.3 s"), labelAt: [830, 221], points: [[710, 221], [880, 221], [880, 284], [950, 284]] },
      { id: "base-r2", from: "base", to: "r2", points: [[710, 296], [950, 296]] },
      { id: "know-r2", from: "know", to: "r2", points: [[710, 371], [880, 371], [880, 308], [950, 308]] },
    ],
  };
}
export const mcpScenario: FlowScenario = { route: ["q2-srv", "srv-perso", "perso-r2"] };

/* 3. Ce qui reste chez toi --------------------------------------------------------------------------- */
export function localDiagram(lang: Lang): FlowDiagramDef {
  const L = (fr: string, en: string) => t(lang, { fr, en });
  return {
    width: 1200,
    height: 290,
    zones: [
      { label: L("Sur ton PC", "On your PC"), x: 0, w: 865 },
      { label: L("Chez le fournisseur de l'IA", "At the AI provider"), x: 885, w: 315 },
    ],
    nodes: [
      { id: "game", label: "WoW Forever", sublabel: L("le jeu tourne", "the game runs"), kind: "step", x: 20, y: 56, w: 170, h: 64 },
      { id: "addon", label: "Addon ForeverScribe", sublabel: L("lit l'API, rien en combat", "reads the API, not in combat"), kind: "step", x: 235, y: 56, w: 190, h: 64 },
      { id: "sv", label: "SavedVariables", sublabel: L("fichier sur ton disque", "file on your disk"), kind: "store", x: 470, y: 56, w: 170, h: 64 },
      { id: "files", label: L("Fichiers du client", "Client files"), sublabel: L("lus, jamais modifiés", "read, never modified"), kind: "store", x: 20, y: 186, w: 170, h: 64 },
      { id: "srv", label: L("Serveur forever", "forever server"), sublabel: L("Python, local", "Python, local"), kind: "step", x: 680, y: 56, w: 160, h: 64 },
      { id: "ai", label: L("Ton assistant", "Your assistant"), sublabel: "Claude Code", kind: "step", x: 960, y: 56, w: 220, h: 64 },
      { id: "web", label: "Web", sublabel: L("seulement si besoin", "only when needed"), kind: "step", x: 960, y: 186, w: 220, h: 64 },
    ],
    edges: [
      { id: "game-addon", from: "game", to: "addon", label: "/sync", labelAt: [212, 76], points: [[190, 88], [235, 88]] },
      { id: "addon-sv", from: "addon", to: "sv", points: [[425, 88], [470, 88]] },
      { id: "sv-srv", from: "sv", to: "srv", points: [[640, 88], [680, 88]] },
      { id: "files-srv", from: "files", to: "srv", label: L("base du jeu, cartes", "game data, maps"), labelAt: [470, 218], points: [[190, 218], [760, 218], [760, 120]] },
      { id: "srv-ai", from: "srv", to: "ai", label: L("résultats", "results"), labelAt: [905, 70], points: [[840, 88], [960, 88]] },
      { id: "ai-web", from: "ai", to: "web", label: L("si besoin", "if needed"), labelAt: [1070, 153], points: [[1070, 120], [1070, 186]] },
    ],
  };
}
export const localScenario: FlowScenario = { route: ["game-addon", "addon-sv", "sv-srv", "srv-ai"] };
