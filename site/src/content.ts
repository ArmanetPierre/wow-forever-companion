// Tout le texte du site, en français et en anglais. Chaque chiffre vient de docs/marketing/arguments.md
// ou de docs/comparaison/bilan.md (comparatif à l'aveugle du 18/11/2026). Perso d'exemple : Brannok (fictif).

export type Lang = "fr" | "en";

export const REPO = "https://github.com/ArmanetPierre/wow-forever-companion";
export const RELEASES = `${REPO}/releases/latest/download`;
export const DL = {
  mac: `${RELEASES}/WoW-Forever-Companion-macOS.zip`,
  win: `${RELEASES}/WoW-Forever-Companion-Windows.zip`,
};
export const ONE_LINER = {
  unix: "curl -fsSL https://raw.githubusercontent.com/ArmanetPierre/wow-forever-companion/main/install/install.sh | bash",
  win: "irm https://raw.githubusercontent.com/ArmanetPierre/wow-forever-companion/main/install/install.ps1 | iex",
};
export const BILAN = `${REPO}/blob/main/docs/comparaison/bilan.md`;

/** Une ligne d'infobulle : `kind` choisit la couleur (conventions des infobulles d'objet). */
export type TipLine =
  | { kind: "bind" | "meta" | "text" | "source"; text: string }
  | { kind: "use"; text: string; way?: string };

export interface Tip {
  /** Qualité : couleur du nom. */
  quality: "uncommon" | "rare" | "epic" | "legendary";
  name: string;
  lines: TipLine[];
}

export interface Pillar {
  id: string;
  title: string;
  stat: string;
  statLabel: string;
  body: string;
  tip: Tip;
  /** Vraie carte zoomée, avec la légende de chaque repère. */
  map?: { label: string; legend: string[] };
}

export interface Persona {
  id: string;
  tab: string;
  blocker: string;
  brings: string;
  question: string;
  /** Pastille de contexte (ex. : mode encore à venir). */
  badge?: string;
  tip?: Tip;
  reads?: string[];
}

const fr = {
  meta: {
    title: "WoW Forever Companion · ton compagnon de guilde pour WoW Forever",
    description:
      "Un compagnon IA pour World of Warcraft: Forever. Il lit ton perso et les données de ton client, et te répond comme un pote de guilde : le verdict, les chiffres, le /way. Gratuit et open source.",
  },
  skip: "Aller au contenu",
  nav: {
    label: "Navigation principale",
    why: "Pourquoi",
    compare: "Comparatif",
    how: "Comment ça marche",
    examples: "Exemples",
    install: "Installer",
    faq: "FAQ",
    github: "Code source sur GitHub",
    lang: "Langue",
    menu: "Menu",
    cta: "Installer",
  },
  hero: {
    title: ["Ton guide", "taillé pour ton perso."],
    lead: "Des conseils personnalisés pour profiter au mieux de WoW Forever. Le compagnon lit ton perso et les données de ton client, puis te répond comme un pote de guilde : quoi faire, où aller, avec le /way et la carte.",
    download: { mac: "Télécharger pour macOS", win: "Télécharger pour Windows", linux: "Installer sur Linux" },
    others: "Autres systèmes",
    mobile: "À installer sur ton ordinateur",
    copyLink: "Copier le lien",
    linkCopied: "Lien copié",
    see: "Voir une réponse",
    fine: "Gratuit et open source (MIT). Fonctionne avec Claude Code.",
    question: "Je fais quoi maintenant ?",
    tip: {
      quality: "epic",
      name: "Réponse du compagnon",
      lines: [
        { kind: "bind", text: "Lié à Brannok, Nain Chasseur 25" },
        { kind: "meta", text: "Les Paluns · synchro il y a 3 min" },
        { kind: "text", text: "Rends d'abord tes 13 quêtes terminées, dont 4 ici aux Paluns : c'est de l'XP gratuite, et ton journal est plein de toute façon." },
        { kind: "use", text: "La vengeance d'Ormer, chez Ormer Ironbraid", way: "/way 38.2 50.9" },
        { kind: "use", text: "Découverte du passé, chez le Prospecteur Whelgar", way: "/way 38.8 52.4" },
        { kind: "source", text: "Addon + QuestieDB · sûr" },
      ],
    } satisfies Tip,
    mapLabel: "Carte stylisée des Paluns avec deux repères numérotés et la position de Brannok",
    mapLegend: ["Ormer Ironbraid", "Prospecteur Whelgar", "Toi"],
    use: "Utiliser :",
    who: "Brannok",
    showAnswer: "Revoir la réponse",
    copied: "Copié",
    copy: "Copier",
  },
  problem: {
    title: "Un chatbot répond de mémoire. De mémoire Classic.",
    lead: "Forever a une nouvelle race, de nouveaux donjons, des objets revus et ses propres quêtes. Une IA généraliste ne voit ni ton perso, ni ton client. Le compagnon, si.",
    head: ["", "Un chatbot", "Le compagnon"],
    rows: [
      ["Ton perso", "« Tu es de quel niveau ? »", "Lit ton niveau, ton stuff, tes talents, ton journal, ton familier, tes sacs et tes métiers."],
      ["Les données du jeu", "Des stats Classic, de mémoire", "Objets, recettes, donjons et table d'XP lus dans ton client Forever et ses correctifs."],
      ["Quêtes et PNJ", "« Quelque part aux Paluns »", "Donneur, receveur et objectifs en /way. Les quêtes ajoutées par Forever s'apprennent en jouant."],
      ["Honnêteté", "Tout sonne aussi sûr", "Chaque info dit d'où elle vient et à quel point elle est sûre."],
      ["Le ton", "« Excellente question ! »", "Comme ton pote de guilde : le verdict d'abord, les chiffres exacts, pas de blabla."],
    ],
  },
  pillars: {
    title: "Trois choses qu'il fait mieux que les autres",
    items: [
      {
        id: "perso",
        title: "Il lit ton perso",
        stat: "12/12",
        statLabel: "sur les questions liées au perso, contre 3,0 à 7,8 en moyenne pour ChatGPT et Gemini",
        body: "Pas de fiche à recopier, pas de questions de contexte. Il voit les 13 quêtes à rendre dans un journal plein, les points de dressage qui dorment, les ingrédients gardés pour une quête.",
        tip: {
          quality: "rare",
          name: "Mon félin : je lui donne quoi ?",
          lines: [
            { kind: "bind", text: "Lié à Brannok, Nain Chasseur 25" },
            { kind: "text", text: "Tu as 120 points de dressage, dont 44 libres. Ne lui donne pas les 3 ingrédients de la Goulash des Carmines : ils sont pour ta quête." },
            { kind: "source", text: "Addon · sûr" },
          ],
        } satisfies Tip,
      },
      {
        id: "way",
        title: "Des /way exacts, et la carte",
        stat: "80 313",
        statLabel: "positions de PNJ et d'objets dans ta base locale",
        body: "Il te donne l'endroit précis, prêt à coller dans le chat. L'outil map dessine la carte de la zone à partir de ton client, avec un repère numéroté par point.",
        map: {
          label: "Carte des Paluns tirée du client du jeu, zoomée sur les Excavations de Whelgar : les quatre fragments et le Prospecteur Whelgar",
          legend: ["Ados, Relique ancienne · /way 34.1 49.9", "Modr, Relique ancienne · /way 34.3 45.7", "Golm, Relique ancienne · /way 35.5 46.2", "Neru, Terre meuble · /way 33.1 46.4", "Prospecteur Whelgar · /way 38.8 52.4"],
        },
        tip: {
          quality: "rare",
          name: "Je trouve pas les fragments",
          lines: [
            { kind: "meta", text: "Découverte du passé · Les Paluns" },
            { kind: "text", text: "Les 4 sont dans l'Excavation. Trois dans des Reliques anciennes, le dernier dans une Terre meuble." },
            { kind: "use", text: "Premier fragment", way: "/way 34.1 49.9" },
            { kind: "use", text: "Dernier fragment", way: "/way 33.1 46.4" },
            { kind: "use", text: "Retour chez Whelgar", way: "/way 38.8 52.4" },
            { kind: "source", text: "QuestieDB · sûr" },
          ],
        } satisfies Tip,
      },
      {
        id: "honest",
        title: "Il ne bluffe pas",
        stat: "0",
        statLabel: "piège Classic et 0 invention grave sur les 12 questions du comparatif",
        body: "Quand une info vient de Classic ou n'est pas encore connue, il le dit au lieu d'inventer. Gemini, sans fiche, a fait de Forever un « serveur privé WotLK 3.3.5 ».",
        tip: {
          quality: "uncommon",
          name: "Le butin de ce boss ?",
          lines: [
            { kind: "text", text: "Le butin de ce boss vient de QuestieDB, donc de Classic : Forever a revu des loots." },
            { kind: "source", text: "À vérifier en jeu" },
          ],
        } satisfies Tip,
      },
    ] as Pillar[],
  },
  compare: {
    title: "Face à ChatGPT et Gemini",
    lead: "On a posé les mêmes 12 questions aux trois, puis fait noter les 60 réponses à l'aveugle, sur 12. ChatGPT est un vrai concurrent : on montre aussi où il fait jeu égal.",
    caption: "Comparatif à l'aveugle du 18/11/2026, notes sur 12",
    cols: ["", "Compagnon", "ChatGPT", "Gemini"],
    sub: ["", "", "sans / avec fiche", "sans / avec fiche"],
    rows: [
      ["Moyenne", "11,8", "7,8 / 8,6", "6,1 / 8,2"],
      ["Questions liées au perso", "12", "5,2 / 7,8", "3,0 / 7,8"],
      ["Actualité de Forever", "11,7", "meilleure : 10 à 11", "meilleure : 8 à 11"],
      ["Pièges Classic tombés", "0", "1 / 0", "3 / 1"],
      ["Inventions graves", "0", "2 / 2", "3 / 1"],
      ["Temps de réponse", "10 à 24 s, mesuré", "10 à 20 s, observé", "même ordre, observé"],
    ],
    note: "« Fiche » : une description du perso écrite à la main et collée avant la question. Pour l'actualité, la note de la meilleure réponse selon la question. Un seul tirage par question, offres gratuites, le 18/11/2026.",
    key: "ChatGPT et Gemini : sans fiche / avec fiche",
    duelsTitle: "Même question, deux réponses",
    duels: [
      {
        q: "« Je trouve pas les fragments de tablette, ils sont où ? »",
        them: { who: "Gemini, sans fiche", score: "2/12", text: "Présente Forever comme un serveur privé WotLK 3.3.5 et conseille de vider le dossier Cache." },
        us: { score: "12/12", text: "Les 4 fragments, l'objet à fouiller pour chacun, un /way par fragment, puis le /way de Whelgar." },
      },
      {
        q: "« Mon félin : je lui donne quoi et je mets où mes points de dressage ? »",
        them: { who: "Gemini, sans fiche", score: "1/12", text: "Confond points de dressage et points de talent, et propose un arbre avec des talents mal nommés." },
        us: { score: "12/12", text: "120 points dont 44 libres, et garde les 3 ingrédients de la Goulash des Carmines pour ta quête." },
      },
      {
        q: "« Je fais quoi maintenant ? »",
        them: { who: "ChatGPT, sans fiche", score: "4/12", text: "Un circuit en 7 étapes, dont 5 quêtes introuvables dans les données du jeu, sans un seul /way." },
        us: { score: "12/12", text: "Rends d'abord tes 13 quêtes terminées : ton journal est plein. Avec les PNJ et les /way." },
      },
    ],
    fair: {
      title: "Là où ChatGPT fait aussi bien",
      q: "« Les Éolides, c'est quelles classes ? »",
      text: "ChatGPT a 11/12 : classes par faction, île de Zéphras, niveaux 1 à 12, pack requis. Juste et sourcé. Le compagnon a 12/12, surtout parce qu'il est plus court. Sur l'actualité (GDKP, raids, Éolides), le web suffit souvent.",
    },
    honest: {
      title: "Ce qu'on ne dit pas",
      items: [
        "Qu'il est plus rapide. Le temps brut est comparable, et ChatGPT commence à écrire plus tôt.",
        "Que ChatGPT se trompe sur tout. Sur les annonces, il a 10 à 11 sur 12.",
        "Que la note est neutre. Le juge est un modèle Claude, comme le compagnon, et les références partagent ses sources.",
        "Que c'est pour le téléphone. ChatGPT est gratuit, sur mobile, avec la voix : le compagnon se sert à l'ordinateur.",
      ],
    },
    more: "Lire le bilan complet, avec les 60 réponses",
  },
  how: {
    title: "Comment il répond",
    lead: "Il lit d'abord ce qu'il a sur ton PC. Le web n'arrive qu'en dernier, et ce qu'il y trouve est gardé pour la fois suivante.",
    pick: "Choisis un exemple",
    scenarios: {
      quete: { label: "Une quête", caption: "« Je trouve pas les fragments de tablette » : ton journal, puis les /way de la base, sans web." },
      regle: { label: "Une règle Forever", caption: "« Les GDKP sont interdits ? » : connaissance Forever sourcée et datée, sans web." },
      nouveau: { label: "Une quête inconnue", caption: "Une quête ajoutée par Forever, absente de la base : Wowhead, puis gardée en local." },
    },
    figure: "Parcours d'une question dans le compagnon",
    stopped: "arrêt",
    branch: "Autre branche :",
    pathTitle: "Le parcours de cet exemple",
    others: "Les autres embranchements",
    ifLabel: (l: string) => `si ${l} :`,
    then: "puis :",
    back: (n: number, name: string) => `Retour à l'étape ${n}, ${name}`,
    legend: { decision: "question qu'il se pose", step: "étape", store: "source de données", route: "parcours de l'exemple" },
    vsTitle: "Avec ou sans le serveur MCP",
    vsLead: "Même question. La différence : le compagnon a un accès direct à ton perso et aux données du jeu, par son serveur local.",
    vsFigure: "Assistant généraliste comparé au compagnon et son serveur",
    vsLegend: { step: "étape", store: "source", route: "parcours du compagnon" },
    scopeTitle: "Ce qu'il sait, ce qu'il va chercher, ce qu'il signale",
    scope: [
      { title: "Il le sait, chez toi, sans Internet", items: ["Ton perso : niveau, stuff, sacs, quêtes, familier", "La base du jeu : objets, quêtes, PNJ, /way", "60 cartes de zone tirées du client", "Les règles de Forever : raids, rulesets, GDKP, Éolides", "Tes notes et ses trouvailles déjà enregistrées"] },
      { title: "Il va le chercher", items: ["Wowhead Forever, pour une quête absente de la base", "Le web, pour une annonce ou un détail manquant", "Puis il le garde, en cache local ou dans tes notes"] },
      { title: "Il te prévient", items: ["Les quêtes ajoutées par Forever, apprises en jouant", "Le butin des boss, qui vient de Classic", "Les annonces du jour pas encore enregistrées", "Ce que personne ne sait encore, comme l'entrée de Krol'dok"] },
    ],
  },
  examples: {
    title: "Pose ta question comme à un pote",
    lead: "Six joueurs, six façons de jouer. Toutes les réponses sont celles du compagnon, sur le perso d'exemple Brannok.",
    tabsLabel: "Profils de joueurs",
    blocker: "Ce qui le bloque",
    brings: "Ce que le compagnon lui apporte",
    reads: "Ce qu'il regarde",
    personas: [
      {
        id: "leveling",
        tab: "Leveling",
        blocker: "Alt-tab sur Wowhead, guides Classic faux pour Forever.",
        brings: "Les quêtes dispo autour de lui, à rendre d'abord, avec /way.",
        question: "Je fais quoi maintenant ?",
        tip: {
          quality: "epic",
          name: "Je fais quoi maintenant ?",
          lines: [
            { kind: "text", text: "Rends d'abord tes 13 quêtes terminées, dont 4 ici aux Paluns : c'est de l'XP gratuite, et ton journal est plein de toute façon." },
            { kind: "use", text: "La vengeance d'Ormer", way: "/way 38.2 50.9" },
            { kind: "use", text: "Découverte du passé", way: "/way 38.8 52.4" },
            { kind: "source", text: "QuestieDB · sûr" },
          ],
        },
      },
      {
        id: "hardcore",
        tab: "Hardcore",
        badge: "Dès l'ouverture du mode HC (hiver 2026/27)",
        blocker: "Une mauvaise info coûte le perso.",
        brings: "La mise en garde en premier (niveau des mobs, élites, JcJ), avec la certitude affichée.",
        question: "Je peux faire L'équipage maudit seul ?",
        tip: {
          quality: "legendary",
          name: "Je peux la faire seul ?",
          lines: [
            { kind: "text", text: "Non, pas à 25 en HC. Mobs 26 à 28, un à trois niveaux au-dessus de toi. Ça, c'est le genre de pull qui te coûte le perso. Reviens à 27 ou en groupe." },
            { kind: "source", text: "QuestieDB · sûr" },
          ],
        },
      },
      {
        id: "craft",
        tab: "Crafteur",
        blocker: "Quel rang, quelle recette donne encore des points, quels composants.",
        brings: "Les recettes connues et leur couleur, les composants dans les sacs et la banque.",
        question: "Comment passer de 106 à 150 en Travail du cuir ?",
        reads: ["Ton rang et ta compétence actuels", "Les recettes que tu connais, et leur couleur", "Les composants dans tes sacs et ta banque", "Les recettes du jeu, lues dans ton client"],
      },
      {
        id: "hunter",
        tab: "Chasseur",
        blocker: "Bonheur, nourriture et points de dressage du familier.",
        brings: "L'état réel du familier, croisé avec la nourriture dans les sacs.",
        question: "Mon familier est content ?",
        tip: {
          quality: "rare",
          name: "Mon familier est content ?",
          lines: [
            { kind: "text", text: "Oui : ton félin est heureux (125 % de dégâts), mais tu as 44 points de dressage qui dorment. Passe voir un dresseur de familiers." },
            { kind: "text", text: "Il mange viande et poisson, et tu as 10 Poisson-lune sauté dans les sacs pour la suite." },
            { kind: "source", text: "Addon · sûr" },
          ],
        },
      },
      {
        id: "friends",
        tab: "Entre amis",
        blocker: "Chacun cherche dans son coin.",
        brings: "Le même outil pour tous, des données séparées, des notes et objectifs par perso.",
        question: "Compare mon stuff avec celui de mon mage.",
        reads: ["Chaque perso de chaque compte, sur ta machine", "Les données de tes amis restent chez eux", "Tes notes et objectifs, perso par perso"],
      },
      {
        id: "english",
        tab: "En anglais",
        blocker: "Outils et guides en français ou pour Classic.",
        brings: "Client enUS ou frFR, réponse dans la langue de ta question, noms du jeu tels quels.",
        question: "The Cursed Crew?",
        tip: {
          quality: "rare",
          name: "The Cursed Crew?",
          lines: [
            { kind: "text", text: "Mobs are 26 to 28 around here, a bit high for you, bring a friend. Snellig's Snuffbox drops from First Mate Snellig." },
            { kind: "use", text: "Cursed crew", way: "/way 14.0 30.2" },
            { kind: "source", text: "QuestieDB · confirmed" },
          ],
        },
      },
    ] satisfies Persona[],
  },
  privacy: {
    title: "Tout reste chez toi",
    lead: "L'addon et le serveur tournent sur ton PC. Seuls ta question et les résultats des outils partent vers ton assistant.",
    figure: "Circulation des données du compagnon",
    legend: { step: "programme", store: "fichier", route: "chemin de ta question" },
    points: [
      { title: "Il ne joue pas à ta place", text: "L'addon lit l'API du jeu, comme un addon de sacs. Aucune touche automatisée, rien en combat. La synchro demande un geste de ta part." },
      { title: "Tes données restent locales", text: "La capture est un fichier sur ton disque. Aucun identifiant lu, ton numéro de compte est masqué. Celles de tes amis restent chez eux." },
      { title: "Le jeu n'est jamais modifié", text: "Les fichiers du client sont seulement lus pour construire ta base, sur ton disque. Le compagnon ne redistribue rien de Blizzard." },
      { title: "Gratuit et ouvert", text: "Licence MIT, code lisible, serveur en Python sans dépendance. Tu paies seulement ton abonnement Claude Code." },
    ],
  },
  install: {
    title: "Installer en trois étapes",
    lead: "L'installateur pose l'addon dans ton jeu, ajoute le plugin à Claude Code et prépare ton dossier de joueur.",
    osLabel: "Ton système",
    os: { mac: "macOS", win: "Windows", linux: "Linux" },
    download: { mac: "Télécharger pour macOS", win: "Télécharger pour Windows" },
    zip: { mac: "WoW-Forever-Companion-macOS.zip", win: "WoW-Forever-Companion-Windows.zip" },
    orTerminal: "Ou en une ligne dans le terminal",
    orPowershell: "Ou en une ligne dans PowerShell",
    inTerminal: "Dans un terminal",
    linuxOnly: "Sur Linux, une ligne dans le terminal suffit. Le script trouve le jeu dans Wine, Lutris, Proton ou Bottles.",
    stepsLabel: "Étapes d'installation",
    status: { done: "terminée", current: "à faire", upcoming: "ensuite", error: "en échec" },
    steps: {
      mac: [
        { t: "Lance l'installateur", d: "Dézippe, puis double-clique sur « Installer WoW Forever Companion »." },
        { t: "Redémarre le jeu", d: "Puis synchronise en jeu avec Ctrl+Maj+S, ou /sync." },
        { t: "Pose ta question", d: "Ouvre Claude Code dans ~/WowForever et demande : « Je fais quoi maintenant ? »" },
      ],
      win: [
        { t: "Lance l'installateur", d: "Dézippe, puis double-clique sur « Installer WoW Forever Companion »." },
        { t: "Redémarre le jeu", d: "Puis synchronise en jeu avec Ctrl+Maj+S, ou /sync." },
        { t: "Pose ta question", d: "Ouvre Claude Code dans ton dossier WowForever et demande : « Je fais quoi maintenant ? »" },
      ],
      linux: [
        { t: "Colle la commande", d: "Dans un terminal, avec Python 3.9 ou plus." },
        { t: "Redémarre le jeu", d: "Puis synchronise en jeu avec Ctrl+Maj+S, ou /sync." },
        { t: "Pose ta question", d: "Ouvre Claude Code dans ~/WowForever et demande : « Je fais quoi maintenant ? »" },
      ],
    },
    warn: {
      mac: "La première fois, macOS bloque l'app : ouvre Réglages système › Confidentialité et sécurité, puis clique sur « Ouvrir quand même ».",
      win: "Windows SmartScreen peut afficher un avertissement : clique sur « Informations complémentaires », puis « Exécuter quand même ».",
      linux: "Lis toujours un script avant de le lancer : il est court et commenté.",
    },
    geek: "Pour les geeks :",
    geekCmd: "xattr -dr com.apple.quarantine <dossier>",
    needsTitle: "Il te faut",
    needs: [
      { text: "WoW Forever installé" },
      { text: "Claude Code", note: "abonnement Claude ou clé API", href: "https://code.claude.com/docs/fr/setup" },
      { text: "Python 3.9 ou plus", href: "https://www.python.org/downloads/" },
    ],
    checks: "L'installateur vérifie ces prérequis et te propose d'installer Claude Code, si tu confirmes. Il n'installe pas Python.",
    manual: "Installation manuelle et options",
  },
  compat: {
    title: "Avec quel assistant ?",
    lead: "Conçu pour Claude Code. Le serveur suit le standard MCP : d'autres assistants devraient pouvoir s'en servir, mais on ne l'a pas encore testé.",
    head: ["Assistant", "Modèles", "Le compagnon"],
    rows: [
      ["Claude Code", "Claude", "Oui, en un clic"],
      ["GitHub Copilot (VS Code)", "GPT, Claude, Gemini", "Serveur MCP local : pas encore testé"],
      ["OpenAI Codex CLI", "GPT", "Serveur MCP local : pas encore testé"],
      ["Cursor", "GPT, Claude", "Serveur MCP local : pas encore testé"],
      ["Appli ChatGPT", "GPT", "Non : elle n'accepte que des serveurs en ligne"],
    ],
    yes: "Oui",
  },
  captures: {
    title: "En jeu",
    lead: "Ce que tu vois de ton côté : un bouton près de la minicarte, une synchro, et ton journal comme le compagnon le lit.",
    items: [
      { file: "bouton-minicarte", alt: "Le bouton ForeverScribe au bord de la minicarte", caption: "Le bouton ForeverScribe, au bord de la minicarte : un clic, et ton perso est à jour." },
      { file: "synchro", alt: "Le message de ForeverScribe dans le chat après /sync", caption: "/sync ou Ctrl+Maj+S : la capture est écrite, le compagnon la lit." },
      { file: "journal-de-quetes", alt: "Le journal de quêtes ouvert sur Découverte du passé", caption: "Ton journal de quêtes : c'est ce que le compagnon voit quand tu demandes quoi faire." },
      { file: "carte-du-monde", alt: "La carte des Paluns avec le repère du /way", caption: "Le /way collé dans le chat, sur ta carte." },
    ],
  },
  faq: {
    title: "Questions fréquentes",
    items: [
      { q: "Blizzard autorise ça ?", a: "L'addon utilise l'API standard des addons, comme n'importe quel addon de sacs ou de quêtes. Il lit, il n'agit jamais : aucune touche, aucune automatisation, rien en combat, aucune lecture d'écran ou de mémoire. Tes questions se posent en dehors du jeu." },
      { q: "Où vont mes données ?", a: "La capture est un fichier que le jeu écrit sur ton disque, et le serveur la lit en local. Elle n'arrive dans ta session Claude que quand tu poses une question. Aucun identifiant n'est lu, et ton numéro de compte est masqué." },
      { q: "Il va sur Internet ?", a: "La construction de la base télécharge une fois quelques outils et QuestieDB. Ensuite, quand aucune source locale ne connaît une quête, il peut demander l'infobulle publique de Wowhead pour cet identifiant : une requête par identifiant, au plus 3 par appel d'outil, et le résultat est gardé en cache. Tu peux le couper dans ta config (web_lookup)." },
      { q: "Il sait tout sur Forever ?", a: "Non, et il le dit. Les quêtes ajoutées par Forever manquent dans QuestieDB : il s'appuie alors sur la mémoire de l'addon, le texte du client et Wowhead, et marque ses suppositions « probable ». Le butin vient de Classic : à vérifier en jeu." },
      { q: "Je peux le partager avec mes amis ?", a: "Oui, c'est fait pour. Chacun l'installe et garde ses données. Plusieurs comptes et plusieurs persos par ordinateur, ça marche." },
      { q: "Ça coûte combien ?", a: "Le projet est gratuit (MIT). Les réponses passent par ton abonnement Claude Code ou ton usage d'API." },
      { q: "Et sur téléphone ?", a: "Pas pour l'instant. Le compagnon tourne à côté du jeu, sur ton ordinateur." },
    ],
  },
  final: {
    title: "Joue mieux, avec un guide qui te connaît.",
    lead: "Installe-le, synchronise ton perso, et pose ta première question.",
    linux: "Linux : une ligne dans le terminal",
  },
  footer: {
    tagline: "WoW Forever Companion",
    links: { github: "GitHub", license: "Licence MIT", bilan: "Le comparatif", changelog: "Nouveautés" },
    legal: "Projet de fan, non affilié à Blizzard Entertainment. World of Warcraft et Blizzard sont des marques de Blizzard Entertainment, Inc. ChatGPT, Gemini et Claude sont des marques de leurs détenteurs respectifs.",
    credit: "Cartes : client World of Warcraft, © Blizzard Entertainment, utilisées dans le cadre d'un projet de fan non commercial.",
    made: "Fait par des joueurs, pour des joueurs.",
  },
};

export type Content = typeof fr;

const en: Content = {
  meta: {
    title: "WoW Forever Companion · your guildmate for WoW Forever",
    description:
      "An AI companion for World of Warcraft: Forever. It reads your character and your client's data, and answers like a guildmate: the verdict, the numbers, the /way. Free and open source.",
  },
  skip: "Skip to content",
  nav: {
    label: "Main navigation",
    why: "Why",
    compare: "Comparison",
    how: "How it works",
    examples: "Examples",
    install: "Install",
    faq: "FAQ",
    github: "Source code on GitHub",
    lang: "Language",
    menu: "Menu",
    cta: "Install",
  },
  hero: {
    title: ["Your guide", "built around your character."],
    lead: "Personalised advice to get the most out of WoW Forever. The companion reads your character and your client's data, then answers like a guildmate: what to do, where to go, with the /way and the map.",
    download: { mac: "Download for macOS", win: "Download for Windows", linux: "Install on Linux" },
    others: "Other systems",
    mobile: "Install it on your computer",
    copyLink: "Copy the link",
    linkCopied: "Link copied",
    see: "See an answer",
    fine: "Free and open source (MIT). Works with Claude Code.",
    question: "What should I do now?",
    tip: {
      quality: "epic",
      name: "Companion's answer",
      lines: [
        { kind: "bind", text: "Bound to Brannok, Dwarf Hunter 25" },
        { kind: "meta", text: "Wetlands · synced 3 min ago" },
        { kind: "text", text: "Turn in your 13 finished quests first, 4 of them right here in the Wetlands: free XP, and your log is full anyway." },
        { kind: "use", text: "Ormer's Revenge, from Ormer Ironbraid", way: "/way 38.2 50.9" },
        { kind: "use", text: "Uncovering the Past, from Prospector Whelgar", way: "/way 38.8 52.4" },
        { kind: "source", text: "Addon + QuestieDB · confirmed" },
      ],
    },
    mapLabel: "Stylised map of the Wetlands with two numbered markers and Brannok's position",
    mapLegend: ["Ormer Ironbraid", "Prospector Whelgar", "You"],
    use: "Use:",
    who: "Brannok",
    showAnswer: "Replay the answer",
    copied: "Copied",
    copy: "Copy",
  },
  problem: {
    title: "A chatbot answers from memory. Classic memory.",
    lead: "Forever has a new race, new dungeons, reworked items and its own quests. A general AI sees neither your character nor your client. The companion does.",
    head: ["", "A chatbot", "The companion"],
    rows: [
      ["Your character", "\"What level are you?\"", "Reads your level, gear, talents, quest log, pet, bags and professions."],
      ["The game's data", "Classic stats, from memory", "Items, recipes, dungeons and the XP table read from your Forever client and its hotfixes."],
      ["Quests and NPCs", "\"Somewhere in the Wetlands\"", "Giver, turn-in and objectives as /way. Quests added by Forever are learned as you play."],
      ["Honesty", "Everything sounds equally sure", "Every fact says where it comes from and how sure it is."],
      ["Tone", "\"Great question!\"", "Like your guildmate: verdict first, exact numbers, no filler."],
    ],
  },
  pillars: {
    title: "Three things it does better",
    items: [
      {
        id: "perso",
        title: "It reads your character",
        stat: "12/12",
        statLabel: "on character questions, against 3.0 to 7.8 on average for ChatGPT and Gemini",
        body: "No sheet to copy, no context questions. It sees the 13 quests to turn in with a full log, the training points left unspent, the ingredients you're keeping for a quest.",
        tip: {
          quality: "rare",
          name: "My cat: what do I feed it?",
          lines: [
            { kind: "bind", text: "Bound to Brannok, Dwarf Hunter 25" },
            { kind: "text", text: "You have 120 training points, 44 of them free. Don't feed it the 3 Redridge Goulash ingredients: they're for your quest." },
            { kind: "source", text: "Addon · confirmed" },
          ],
        },
      },
      {
        id: "way",
        title: "Exact /way, and the map",
        stat: "80,313",
        statLabel: "NPC and object positions in your local database",
        body: "It gives you the exact spot, ready to paste in chat. The map tool draws the zone map from your own client, with one numbered marker per point.",
        map: {
          label: "Wetlands map from the game client, zoomed on Whelgar's Excavation Site: the four fragments and Prospector Whelgar",
          legend: ["Ados, ancient relic · /way 34.1 49.9", "Modr, ancient relic · /way 34.3 45.7", "Golm, ancient relic · /way 35.5 46.2", "Neru, loose soil · /way 33.1 46.4", "Prospector Whelgar · /way 38.8 52.4"],
        },
        tip: {
          quality: "rare",
          name: "Can't find the fragments",
          lines: [
            { kind: "meta", text: "Uncovering the Past · Wetlands" },
            { kind: "text", text: "All 4 are in the dig site: three in ancient relics, the last one in loose soil." },
            { kind: "use", text: "First fragment", way: "/way 34.1 49.9" },
            { kind: "use", text: "Last fragment", way: "/way 33.1 46.4" },
            { kind: "use", text: "Back to Whelgar", way: "/way 38.8 52.4" },
            { kind: "source", text: "QuestieDB · confirmed" },
          ],
        },
      },
      {
        id: "honest",
        title: "It doesn't bluff",
        stat: "0",
        statLabel: "Classic traps and 0 serious made-up facts across the 12 test questions",
        body: "When something comes from Classic or isn't known yet, it says so instead of making it up. Gemini, without a sheet, called Forever a \"WotLK 3.3.5 private server\".",
        tip: {
          quality: "uncommon",
          name: "This boss's loot?",
          lines: [
            { kind: "text", text: "This boss's loot comes from QuestieDB, so from Classic: Forever reworked some loot." },
            { kind: "source", text: "Check in game" },
          ],
        },
      },
    ] as Pillar[],
  },
  compare: {
    title: "Against ChatGPT and Gemini",
    lead: "We asked all three the same 12 questions, then had the 60 answers scored blind, out of 12. ChatGPT is a real competitor: we also show where it's just as good.",
    caption: "Blind test of 18/11/2026, scores out of 12",
    cols: ["", "Companion", "ChatGPT", "Gemini"],
    sub: ["", "", "without / with sheet", "without / with sheet"],
    rows: [
      ["Average", "11.8", "7.8 / 8.6", "6.1 / 8.2"],
      ["Character questions", "12", "5.2 / 7.8", "3.0 / 7.8"],
      ["Forever news", "11.7", "best: 10 to 11", "best: 8 to 11"],
      ["Classic traps fallen into", "0", "1 / 0", "3 / 1"],
      ["Serious made-up facts", "0", "2 / 2", "3 / 1"],
      ["Response time", "10 to 24 s, measured", "10 to 20 s, observed", "similar, observed"],
    ],
    note: "\"Sheet\": a hand-written description of the character pasted before the question. For news, the score of the best answer depending on the question. One run per question, free tiers, on 18/11/2026.",
    key: "ChatGPT and Gemini: without sheet / with sheet",
    duelsTitle: "Same question, two answers",
    duels: [
      {
        q: "\"Can't find the tablet fragments, where are they?\"",
        them: { who: "Gemini, without sheet", score: "2/12", text: "Calls Forever a WotLK 3.3.5 private server and suggests clearing the Cache folder." },
        us: { score: "12/12", text: "The 4 fragments, the object to search for each, one /way per fragment, then Whelgar's /way." },
      },
      {
        q: "\"My cat: what do I feed it and where do my training points go?\"",
        them: { who: "Gemini, without sheet", score: "1/12", text: "Mixes up pet training points and talent points, and offers a tree with misnamed talents." },
        us: { score: "12/12", text: "120 points, 44 free, and keep the 3 Redridge Goulash ingredients for your quest." },
      },
      {
        q: "\"What should I do now?\"",
        them: { who: "ChatGPT, without sheet", score: "4/12", text: "A 7-step route including 5 quests that can't be found in the game data, and not a single /way." },
        us: { score: "12/12", text: "Turn in your 13 finished quests first: your log is full. With the NPCs and the /way." },
      },
    ],
    fair: {
      title: "Where ChatGPT does just as well",
      q: "\"Eolides: which classes?\"",
      text: "ChatGPT scores 11/12: classes by faction, the isle of Zephras, levels 1 to 12, pack required. Right and sourced. The companion scores 12/12, mostly for being shorter. On news (GDKP, raids, Eolides), the web is often enough.",
    },
    honest: {
      title: "What we don't claim",
      items: [
        "That it's faster. Raw time is similar, and ChatGPT starts writing sooner.",
        "That ChatGPT gets everything wrong. On announcements it scores 10 to 11 out of 12.",
        "That the score is neutral. The judge is a Claude model, like the companion, and the references share its sources.",
        "That it's for your phone. ChatGPT is free, on mobile, with voice: the companion runs on your computer.",
      ],
    },
    more: "Read the full report, with all 60 answers",
  },
  how: {
    title: "How it answers",
    lead: "It reads what's on your PC first. The web comes last, and what it finds there is kept for next time.",
    pick: "Pick an example",
    scenarios: {
      quete: { label: "A quest", caption: "\"Can't find the tablet fragments\": your log, then the /way from the database, no web." },
      regle: { label: "A Forever rule", caption: "\"Are GDKPs banned?\": sourced and dated Forever knowledge, no web." },
      nouveau: { label: "An unknown quest", caption: "A quest added by Forever, missing from the database: Wowhead, then kept locally." },
    },
    figure: "How a question flows through the companion",
    stopped: "stop",
    branch: "Other branch:",
    pathTitle: "This example's path",
    others: "The other branches",
    ifLabel: (l: string) => `if ${l}:`,
    then: "then:",
    back: (n: number, name: string) => `Back to step ${n}, ${name}`,
    legend: { decision: "question it asks itself", step: "step", store: "data source", route: "example path" },
    vsTitle: "With or without the MCP server",
    vsLead: "Same question. The difference: the companion has direct access to your character and the game data, through its local server.",
    vsFigure: "General assistant compared with the companion and its server",
    vsLegend: { step: "step", store: "source", route: "companion's path" },
    scopeTitle: "What it knows, what it looks up, what it flags",
    scope: [
      { title: "It knows it, on your PC, offline", items: ["Your character: level, gear, bags, quests, pet", "The game database: items, quests, NPCs, /way", "60 zone maps from your client", "Forever's rules: raids, rulesets, GDKP, Eolides", "Your notes and its saved findings"] },
      { title: "It looks it up", items: ["Wowhead Forever, for a quest missing from the database", "The web, for an announcement or a missing detail", "Then it keeps it, in a local cache or your notes"] },
      { title: "It warns you", items: ["Quests added by Forever, learned as you play", "Boss loot, which comes from Classic", "Same-day announcements not saved yet", "What nobody knows yet, like Krol'dok's entrance"] },
    ],
  },
  examples: {
    title: "Ask like you'd ask a friend",
    lead: "Six players, six ways to play. Every answer is the companion's, on the sample character Brannok.",
    tabsLabel: "Player profiles",
    blocker: "What slows them down",
    brings: "What the companion gives them",
    reads: "What it looks at",
    personas: [
      {
        id: "leveling",
        tab: "Leveling",
        blocker: "Alt-tabbing to Wowhead, Classic guides that are wrong for Forever.",
        brings: "Quests available nearby, turn-ins first, with /way.",
        question: "What should I do now?",
        tip: {
          quality: "epic",
          name: "What should I do now?",
          lines: [
            { kind: "text", text: "Turn in your 13 finished quests first, 4 of them right here in the Wetlands: free XP, and your log is full anyway." },
            { kind: "use", text: "Ormer's Revenge", way: "/way 38.2 50.9" },
            { kind: "use", text: "Uncovering the Past", way: "/way 38.8 52.4" },
            { kind: "source", text: "QuestieDB · confirmed" },
          ],
        },
      },
      {
        id: "hardcore",
        tab: "Hardcore",
        badge: "Once HC mode opens (winter 2026/27)",
        blocker: "One bad tip costs the character.",
        brings: "The warning first (mob levels, elites, PvP), with the certainty shown.",
        question: "Can I solo The Cursed Crew?",
        tip: {
          quality: "legendary",
          name: "Can I solo it?",
          lines: [
            { kind: "text", text: "No, not at 25 in HC. Mobs are 26 to 28, one to three levels above you. That's the kind of pull that costs you the character. Come back at 27 or in a group." },
            { kind: "source", text: "QuestieDB · confirmed" },
          ],
        },
      },
      {
        id: "craft",
        tab: "Crafter",
        blocker: "Which rank, which recipe still gives points, which materials.",
        brings: "Known recipes and their colour, materials in bags and bank.",
        question: "How do I get Leatherworking from 106 to 150?",
        reads: ["Your current rank and skill", "The recipes you know, and their colour", "Materials in your bags and bank", "The game's recipes, read from your client"],
      },
      {
        id: "hunter",
        tab: "Hunter",
        blocker: "Pet happiness, food and training points.",
        brings: "The pet's real state, matched with the food in your bags.",
        question: "Is my pet happy?",
        tip: {
          quality: "rare",
          name: "Is my pet happy?",
          lines: [
            { kind: "text", text: "Yes: your cat is happy (125% damage), but you have 44 training points sitting idle. Go see a pet trainer." },
            { kind: "text", text: "It eats meat and fish, and you have 10 Sauteed Sunfish in your bags for later." },
            { kind: "source", text: "Addon · confirmed" },
          ],
        },
      },
      {
        id: "friends",
        tab: "With friends",
        blocker: "Everyone searches on their own.",
        brings: "The same tool for everyone, separate data, notes and goals per character.",
        question: "Compare my gear with my mage's.",
        reads: ["Every character of every account, on your machine", "Your friends' data stays on their machines", "Your notes and goals, character by character"],
      },
      {
        id: "english",
        tab: "In English",
        blocker: "Tools and guides in French, or made for Classic.",
        brings: "enUS or frFR client, answers in your question's language, game names as they are.",
        question: "The Cursed Crew?",
        tip: {
          quality: "rare",
          name: "The Cursed Crew?",
          lines: [
            { kind: "text", text: "Mobs are 26 to 28 around here, a bit high for you, bring a friend. Snellig's Snuffbox drops from First Mate Snellig." },
            { kind: "use", text: "Cursed crew", way: "/way 14.0 30.2" },
            { kind: "source", text: "QuestieDB · confirmed" },
          ],
        },
      },
    ],
  },
  privacy: {
    title: "Everything stays with you",
    lead: "The addon and the server run on your PC. Only your question and the tools' results go to your assistant.",
    figure: "How the companion's data flows",
    legend: { step: "program", store: "file", route: "your question's path" },
    points: [
      { title: "It doesn't play for you", text: "The addon reads the game API, like a bag addon. No automated keys, nothing in combat. Syncing needs a key press from you." },
      { title: "Your data stays local", text: "The capture is a file on your disk. No credentials are read, your account number is masked. Your friends' data stays on their machines." },
      { title: "The game is never modified", text: "Client files are only read to build your database, on your disk. The companion redistributes nothing from Blizzard." },
      { title: "Free and open", text: "MIT licence, readable code, a Python server with no dependencies. You only pay for your Claude Code subscription." },
    ],
  },
  install: {
    title: "Install in three steps",
    lead: "The installer puts the addon in your game, adds the plugin to Claude Code and sets up your player folder.",
    osLabel: "Your system",
    os: { mac: "macOS", win: "Windows", linux: "Linux" },
    download: { mac: "Download for macOS", win: "Download for Windows" },
    zip: { mac: "WoW-Forever-Companion-macOS.zip", win: "WoW-Forever-Companion-Windows.zip" },
    orTerminal: "Or in one line in the terminal",
    orPowershell: "Or in one line in PowerShell",
    inTerminal: "In a terminal",
    linuxOnly: "On Linux, one line in the terminal is enough. The script finds the game in Wine, Lutris, Proton or Bottles.",
    stepsLabel: "Installation steps",
    status: { done: "done", current: "to do", upcoming: "next", error: "failed" },
    steps: {
      mac: [
        { t: "Run the installer", d: "Unzip, then double-click \"Install WoW Forever Companion\"." },
        { t: "Restart the game", d: "Then sync in game with Ctrl+Shift+S, or /sync." },
        { t: "Ask away", d: "Open Claude Code in ~/WowForever and ask: \"What should I do now?\"" },
      ],
      win: [
        { t: "Run the installer", d: "Unzip, then double-click \"Install WoW Forever Companion\"." },
        { t: "Restart the game", d: "Then sync in game with Ctrl+Shift+S, or /sync." },
        { t: "Ask away", d: "Open Claude Code in your WowForever folder and ask: \"What should I do now?\"" },
      ],
      linux: [
        { t: "Paste the command", d: "In a terminal, with Python 3.9 or later." },
        { t: "Restart the game", d: "Then sync in game with Ctrl+Shift+S, or /sync." },
        { t: "Ask away", d: "Open Claude Code in ~/WowForever and ask: \"What should I do now?\"" },
      ],
    },
    warn: {
      mac: "The first time, macOS blocks the app: open System Settings › Privacy & Security, then click \"Open Anyway\".",
      win: "Windows SmartScreen may show a warning: click \"More info\", then \"Run anyway\".",
      linux: "Always read a script before running it: this one is short and commented.",
    },
    geek: "For the geeks:",
    geekCmd: "xattr -dr com.apple.quarantine <folder>",
    needsTitle: "You need",
    needs: [
      { text: "WoW Forever installed" },
      { text: "Claude Code", note: "Claude subscription or API key", href: "https://code.claude.com/docs/en/setup" },
      { text: "Python 3.9 or later", href: "https://www.python.org/downloads/" },
    ],
    checks: "The installer checks these and offers to install Claude Code once you confirm. It doesn't install Python.",
    manual: "Manual install and options",
  },
  compat: {
    title: "Which assistant?",
    lead: "Built for Claude Code. The server follows the MCP standard: other assistants should be able to use it, but we haven't tested them yet.",
    head: ["Assistant", "Models", "The companion"],
    rows: [
      ["Claude Code", "Claude", "Yes, in one click"],
      ["GitHub Copilot (VS Code)", "GPT, Claude, Gemini", "Local MCP server: not tested yet"],
      ["OpenAI Codex CLI", "GPT", "Local MCP server: not tested yet"],
      ["Cursor", "GPT, Claude", "Local MCP server: not tested yet"],
      ["ChatGPT app", "GPT", "No: it only accepts online servers"],
    ],
    yes: "Yes",
  },
  captures: {
    title: "In game",
    lead: "What you see on your side: a button by the minimap, a sync, and your quest log as the companion reads it.",
    items: [
      { file: "bouton-minicarte", alt: "The ForeverScribe button on the edge of the minimap", caption: "The ForeverScribe button, on the edge of the minimap: one click and your character is up to date." },
      { file: "synchro", alt: "ForeverScribe's chat message after /sync", caption: "/sync or Ctrl+Shift+S: the capture is written, the companion reads it." },
      { file: "journal-de-quetes", alt: "The quest log open on Uncovering the Past", caption: "Your quest log: this is what the companion sees when you ask what to do." },
      { file: "carte-du-monde", alt: "The Wetlands map with the /way waypoint", caption: "The /way pasted in chat, on your map." },
    ],
  },
  faq: {
    title: "Frequently asked questions",
    items: [
      { q: "Is this allowed by Blizzard?", a: "The addon uses the standard addon API, like any bag or quest addon. It reads, it never acts: no key presses, no automation, nothing in combat, no screen or memory reading. Your questions are asked outside the game." },
      { q: "Where does my data go?", a: "The capture is a file the game writes on your disk, and the server reads it locally. It reaches your Claude session only when you ask a question. No credentials are read, and your account number is masked." },
      { q: "Does it go online?", a: "Building the database downloads a few tools and QuestieDB once. Then, when no local source knows a quest, it can ask Wowhead's public tooltip for that id: one request per id, at most 3 per tool call, and the result is cached. You can turn it off in your config (web_lookup)." },
      { q: "Does it know everything about Forever?", a: "No, and it says so. Quests added by Forever are missing from QuestieDB: it falls back on the addon's quest memory, the client's text and Wowhead, and marks guesses as \"probable\". Loot comes from Classic: check in game." },
      { q: "Can I share it with friends?", a: "Yes, that's the point. Each player installs it and keeps their own data. Several accounts and characters per computer work fine." },
      { q: "What does it cost?", a: "The project is free (MIT). Answers use your Claude Code subscription or API usage." },
      { q: "What about my phone?", a: "Not for now. The companion runs next to the game, on your computer." },
    ],
  },
  final: {
    title: "Play better, with a guide who knows you.",
    lead: "Install it, sync your character, and ask your first question.",
    linux: "Linux: one line in the terminal",
  },
  footer: {
    tagline: "WoW Forever Companion",
    links: { github: "GitHub", license: "MIT licence", bilan: "The comparison", changelog: "What's new" },
    legal: "Fan project, not affiliated with Blizzard Entertainment. World of Warcraft and Blizzard are trademarks of Blizzard Entertainment, Inc. ChatGPT, Gemini and Claude are trademarks of their respective owners.",
    credit: "Maps: World of Warcraft client, © Blizzard Entertainment, used for a non-commercial fan project.",
    made: "Made by players, for players.",
  },
};

/* ─── Typographie ───────────────────────────────────────────────────────────────────────────────
 * Français : espace fine insécable avant ? ! ; et insécable avant : et dans « ». Anglais : guillemets
 * et apostrophes typographiques. Appliqué à toutes les chaînes, une fois, au chargement. */
const NNBSP = "\u202F";
const NBSP = "\u00A0";
export function typoFr(s: string): string {
  return s
    .replace(/'/g, "’")
    .replace(/« ?/g, `«${NBSP}`)
    .replace(/ ?»/g, `${NBSP}»`)
    .replace(/ ([?!;])/g, `${NNBSP}$1`)
    .replace(/ :(?=\s|$)/g, `${NBSP}:`)
    .replace(/ ›/g, `${NBSP}›`);
}
export function typoEn(s: string): string {
  return s.replace(/'/g, "’").replace(/"([^"]*)"/g, "“$1”");
}
function deep<T>(v: T, f: (s: string) => string): T {
  if (typeof v === "string") return f(v) as T;
  if (Array.isArray(v)) return v.map((x) => deep(x, f)) as T;
  if (v && typeof v === "object") return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, k === "href" || k === "geekCmd" || k === "way" ? x : deep(x, f)])) as T;
  if (typeof v === "function") return ((...a: unknown[]) => f(String((v as (...b: unknown[]) => unknown)(...a)))) as T;
  return v;
}

export const content: Record<Lang, Content> = { fr: deep(fr, typoFr), en: deep(en, typoEn) };
