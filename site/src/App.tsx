import { useEffect, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent, type ReactNode } from "react";
import { FlowDiagram, SegmentedControl, Stepper, type SegOption, type StepDef } from "@ui-kit";
import { BILAN, DL, ONE_LINER, REPO, content, type Lang } from "./content";
import { answerDiagram, answerScenarios, localDiagram, localScenario, mcpDiagram, mcpScenario } from "./diagrams";
import { Tooltip } from "./components/Tooltip";
import { MobileFlow } from "./components/MobileFlow";
import { RealMap } from "./components/RealMap";
import { Frame, GitHubIcon, OsIcon, Rule, Sigil } from "./components/Ornament";

type Os = "mac" | "win" | "linux";

/** Système de l'ordinateur, et si la page est ouverte sur un téléphone ou une tablette (rien à installer là). */
function detectDevice(): { os: Os; mobile: boolean } {
  if (typeof navigator === "undefined") return { os: "mac", mobile: false };
  const nav = navigator as Navigator & { userAgentData?: { platform?: string; mobile?: boolean } };
  const p = `${nav.userAgentData?.platform ?? ""} ${navigator.platform ?? ""} ${navigator.userAgent}`.toLowerCase();
  const ipadOs = p.includes("mac") && navigator.maxTouchPoints > 1;
  const mobile = Boolean(nav.userAgentData?.mobile) || /iphone|ipad|ipod|android/.test(p) || ipadOs;
  if (mobile) return { os: /android/.test(p) ? "win" : "mac", mobile };
  if (p.includes("win")) return { os: "win", mobile };
  if (p.includes("linux") || p.includes("x11") || p.includes("cros")) return { os: "linux", mobile };
  return { os: "mac", mobile };
}

/** « macOS » garde sa casse, sans espacement de lettres. */
function osText(text: string): ReactNode {
  const parts = text.split(/(macOS)/);
  return parts.map((part, i) => (part === "macOS" ? <span key={i} className="osname">macOS</span> : part));
}

function initialLang(): Lang {
  try {
    const saved = localStorage.getItem("wfc-lang");
    if (saved === "fr" || saved === "en") return saved;
  } catch {
    /* stockage indisponible : on suit le navigateur */
  }
  const q = new URLSearchParams(location.search).get("lang");
  if (q === "fr" || q === "en") return q;
  return navigator.language?.toLowerCase().startsWith("fr") ? "fr" : "en";
}

export function App() {
  const [lang, setLang] = useState<Lang>(initialLang);
  const [device] = useState(detectDevice);
  const [os, setOs] = useState<Os>(device.os);
  const [menu, setMenu] = useState(false);
  const menuBtn = useRef<HTMLButtonElement>(null);
  const navRef = useRef<HTMLElement>(null);
  const c = content[lang];

  useEffect(() => {
    document.documentElement.lang = lang;
    document.title = c.meta.title;
    document.querySelector('meta[name="description"]')?.setAttribute("content", c.meta.description);
    try {
      localStorage.setItem("wfc-lang", lang);
    } catch {
      /* rien à faire */
    }
  }, [lang, c]);

  // Menu mobile : Échap rend le focus au bouton, un clic dehors le ferme, la page derrière ne défile pas.
  useEffect(() => {
    if (!menu) return;
    const onKey = (ev: globalThis.KeyboardEvent) => {
      if (ev.key === "Escape") {
        setMenu(false);
        menuBtn.current?.focus();
      }
    };
    const onDown = (ev: PointerEvent) => {
      const t = ev.target as Node;
      if (!navRef.current?.contains(t) && !menuBtn.current?.contains(t)) setMenu(false);
    };
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onDown);
    return () => {
      document.body.style.overflow = prev;
      window.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onDown);
    };
  }, [menu]);
  useEffect(() => {
    const wide = window.matchMedia("(min-width: 1101px)");
    const close = () => wide.matches && setMenu(false);
    wide.addEventListener("change", close);
    return () => wide.removeEventListener("change", close);
  }, []);

  const langs: Array<SegOption<Lang>> = [
    { id: "fr", label: "FR", lang: "fr", title: "Français" },
    { id: "en", label: "EN", lang: "en", title: "English" },
  ];

  const nav = [
    ["why", c.nav.why],
    ["compare", c.nav.compare],
    ["how", c.nav.how],
    ["examples", c.nav.examples],
    ["install", c.nav.install],
    ["faq", c.nav.faq],
  ] as const;

  return (
    <>
      <a className="skip" href="#main">
        {c.skip}
      </a>
      <header className="top">
        <div className="top-in">
          <a className="brand" href="#top" aria-label="WoW Forever Companion">
            <Sigil size={30} />
            <span className="brand-name">
              <span className="bn1">WoW Forever</span> <span className="bn2">Companion</span>
            </span>
          </a>
          <button ref={menuBtn} type="button" className="menu-btn" aria-expanded={menu} aria-controls="nav" onClick={() => setMenu(!menu)}>
            <span className="menu-ico" aria-hidden="true" />
            <span className="sr">{c.nav.menu}</span>
          </button>
          <nav ref={navRef} id="nav" className={`nav${menu ? " open" : ""}`} aria-label={c.nav.label}>
            <ul>
              {nav.map(([id, label]) => (
                <li key={id}>
                  <a href={`#${id}`} onClick={() => setMenu(false)}>
                    {label}
                  </a>
                </li>
              ))}
            </ul>
            <div className="nav-tools">
              <SegmentedControl value={lang} options={langs} onChange={setLang} label={c.nav.lang} className="lang" />
              <a className="gh" href={REPO} aria-label={c.nav.github}>
                <GitHubIcon />
              </a>
              <a className="btn btn-gold top-cta" href="#install">
                {c.nav.cta}
              </a>
            </div>
          </nav>
        </div>
      </header>

      <main id="main">
        <Hero c={c} os={os} mobile={device.mobile} />
        <Problem c={c} />
        <Pillars c={c} />
        <Compare c={c} />
        <How c={c} lang={lang} />
        <Examples c={c} />
        <Privacy c={c} lang={lang} />
        <Install c={c} os={os} setOs={setOs} />
        <Captures c={c} />
        <Compat c={c} />
        <Faq c={c} />
        <Final c={c} />
      </main>

      <footer className="foot">
        <div className="wrap foot-in">
          <div className="foot-brand">
            <Sigil size={36} />
            <p className="foot-tag">{c.footer.tagline}</p>
            <p className="foot-made">{c.footer.made}</p>
          </div>
          <ul className="foot-links">
            <li><a href={REPO}>{c.footer.links.github}</a></li>
            <li><a href={`${REPO}/blob/main/LICENSE`}>{c.footer.links.license}</a></li>
            <li><a href={BILAN}>{c.footer.links.bilan}</a></li>
            <li><a href={`${REPO}/blob/main/CHANGELOG.md`}>{c.footer.links.changelog}</a></li>
          </ul>
          <p className="foot-legal">
            {c.footer.legal}
            <br />
            {c.footer.credit}
          </p>
        </div>
      </footer>
    </>
  );
}

type C = (typeof content)["fr"];

/* ─── Hero ───────────────────────────────────────────────────────────────────────────────────── */
/* Cartes : images du client, exportées par scripts/build-maps.py, recadrées en CSS. */
const MAPS = {
  paluns: `${import.meta.env.BASE_URL}maps/paluns.webp`,
  royaumes: `${import.meta.env.BASE_URL}maps/royaumes-de-l-est.webp`,
};
/** Fenêtre du héros sur Les Paluns : de Menethil au site de fouilles (x, y, largeur, hauteur en %). */
const HERO_VIEW: [number, number, number, number] = [4, 26, 46, 48];
/** /way de l'exemple : Ormer Ironbraid et le Prospecteur Whelgar. Pastilles écartées, le point reste exact. */
const HERO_PINS = [
  { x: 38.2, y: 50.9, n: "1", dx: -26, dy: 4 },
  { x: 38.8, y: 52.4, n: "2", dx: 20, dy: 16 },
];
/** Brannok (fictif) sur la route de Menethil. */
const HERO_ME = { x: 25.5, y: 47.5 };
/** Zoom sur les fouilles : les 4 fragments de « Découverte du passé » et Whelgar. */
const DIG_VIEW: [number, number, number, number] = [27, 38.5, 17, 19];
const DIG_PINS = [
  { x: 34.1, y: 49.9, n: "1" },
  { x: 34.3, y: 45.7, n: "2" },
  { x: 35.5, y: 46.2, n: "3", dx: 14, dy: -12 },
  { x: 33.1, y: 46.4, n: "4", dx: -14, dy: 8 },
  { x: 38.8, y: 52.4, n: "W" },
];

function Hero({ c, os, mobile }: { c: C; os: Os; mobile: boolean }) {
  const href = mobile || os === "linux" ? "#install" : DL[os];
  const [hot, setHot] = useState<number | null>(null);
  return (
    <section className="hero" id="top" aria-labelledby="hero-title">
      <div className="hero-sky" aria-hidden="true" />
      <div className="hero-atlas" aria-hidden="true" style={{ backgroundImage: `url(${MAPS.royaumes})` }} />
      <div className="wrap hero-in">
        <div className="hero-copy">
          <h1 id="hero-title" className="hero-title">
            <span className="l1">{c.hero.title[0]}</span>
            <span className="l2">{c.hero.title[1]}</span>
          </h1>
          <p className="hero-lead">{c.hero.lead}</p>
          <div className="hero-cta">
            <a className="btn btn-gold" href={href}>
              {mobile ? null : <OsIcon os={os} />}
              <span>{mobile ? c.hero.mobile : osText(c.hero.download[os])}</span>
            </a>
            {mobile ? <CopyPageLink label={c.hero.copyLink} done={c.hero.linkCopied} /> : (
              <a className="btn btn-ghost" href="#examples">
                {c.hero.see}
              </a>
            )}
          </div>
          <p className="hero-fine">
            {c.hero.fine} <a href="#install">{c.hero.others}</a>
          </p>
        </div>
        <div className="hero-art">
          <RealMap
            className="hero-map"
            src={MAPS.paluns}
            view={HERO_VIEW}
            label={c.hero.mapLabel}
            pins={HERO_PINS}
            me={HERO_ME}
            hot={hot}
            loading="eager"
          >
            <figcaption className="map-legend">
              <span><i className="pin">1</i>{c.hero.mapLegend[0]}</span>
              <span><i className="pin">2</i>{c.hero.mapLegend[1]}</span>
              <span><i className="me" />{c.hero.mapLegend[2]}</span>
            </figcaption>
          </RealMap>
          <Tooltip
            className="hero-tip"
            tip={c.hero.tip}
            question={c.hero.question}
            onWay={setHot}
            hot={hot}
            useLabel={c.hero.use}
            copyLabel={c.hero.copy}
            copiedLabel={c.hero.copied}
          />
        </div>
      </div>
    </section>
  );
}

/* ─── Le problème ───────────────────────────────────────────────────────────────────────────── */
function Problem({ c }: { c: C }) {
  return (
    <section className="sec" id="why" aria-labelledby="why-title">
      <div className="wrap">
        <header className="sec-head">
          <h2 id="why-title">{c.problem.title}</h2>
          <Rule />
          <p className="sec-lead">{c.problem.lead}</p>
        </header>
        <div className="duel" role="table" aria-labelledby="why-title">
          <div className="duel-row duel-head" role="row">
            {c.problem.head.map((h, i) => (
              <span key={i} role="columnheader" className={i === 0 ? "duel-k" : i === 1 ? "duel-them" : "duel-us"}>
                {h}
              </span>
            ))}
          </div>
          {c.problem.rows.map(([k, them, us]) => (
            <div className="duel-row" role="row" key={k}>
              <span role="rowheader" className="duel-k">{k}</span>
              <span role="cell" className="duel-them" data-label={c.problem.head[1]}>{them}</span>
              <span role="cell" className="duel-us" data-label={c.problem.head[2]}>{us}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── Les 3 atouts ──────────────────────────────────────────────────────────────────────────── */
function Pillars({ c }: { c: C }) {
  return (
    <section className="sec sec-pillars" aria-labelledby="pillars-title">
      <div className="wrap">
        <header className="sec-head">
          <h2 id="pillars-title">{c.pillars.title}</h2>
          <Rule />
        </header>
        <div className="pillars">
          {c.pillars.items.map((p) => (
            <article className={`pillar p-${p.id}`} key={p.id}>
              <h3>{p.title}</h3>
              <p className="pillar-stat">
                <strong>{p.stat}</strong>
                <span>{p.statLabel}</span>
              </p>
              <p className="pillar-body">{p.body}</p>
              <div className="pillar-answer">
              {p.map && (
                <RealMap className="dig-map" src={MAPS.paluns} view={DIG_VIEW} label={p.map.label} pins={DIG_PINS}>
                  <figcaption className="map-legend dig-legend">
                    {p.map.legend.map((t, i) => (
                      <span key={t}>
                        <i className="pin">{DIG_PINS[i]?.n}</i>
                        {t}
                      </span>
                    ))}
                  </figcaption>
                </RealMap>
              )}
              <Tooltip tip={p.tip} live replayLabel={c.hero.showAnswer} useLabel={c.hero.use} copyLabel={c.hero.copy} copiedLabel={c.hero.copied} />
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── Comparatif ────────────────────────────────────────────────────────────────────────────── */
function Compare({ c }: { c: C }) {
  const k = c.compare;
  return (
    <section className="sec sec-compare" id="compare" aria-labelledby="compare-title">
      <div className="wrap">
        <header className="sec-head">
          <h2 id="compare-title">{k.title}</h2>
          <Rule />
          <p className="sec-lead">{k.lead}</p>
        </header>

        <Ledger k={k} />

        <h3 className="sub-title">{k.duelsTitle}</h3>
        <div className="duels">
          {k.duels.map((d) => (
            <article className="vs" key={d.q}>
              <p className="vs-q">{d.q}</p>
              <div className="vs-them">
                <p className="vs-who">
                  {d.them.who} <span className="score low">{d.them.score}</span>
                </p>
                <p>{d.them.text}</p>
              </div>
              <div className="vs-us">
                <p className="vs-who">
                  {c === content.fr ? "Compagnon" : "Companion"} <span className="score high">{d.us.score}</span>
                </p>
                <p>{d.us.text}</p>
              </div>
            </article>
          ))}
        </div>

        <div className="fair-row">
          <article className="fair">
            <h3>{k.fair.title}</h3>
            <p className="vs-q">{k.fair.q}</p>
            <p>{k.fair.text}</p>
          </article>
          <article className="honest">
            <h3>{k.honest.title}</h3>
            <ul>
              {k.honest.items.map((i) => (
                <li key={i}>{i}</li>
              ))}
            </ul>
          </article>
        </div>
        <p className="more">
          <a href={BILAN}>{k.more}</a>
        </p>
      </div>
    </section>
  );
}

/* ─── Comment il répond ─────────────────────────────────────────────────────────────────────── */
function How({ c, lang }: { c: C; lang: Lang }) {
  type Sc = keyof typeof answerScenarios;
  const [sc, setSc] = useState<Sc>("quete");
  const h = c.how;
  const diagram = useMemo(() => answerDiagram(lang), [lang]);
  const vs = useMemo(() => mcpDiagram(lang), [lang]);
  const options: Array<SegOption<Sc>> = (["quete", "regle", "nouveau"] as const).map((id) => ({ id, label: h.scenarios[id].label }));
  return (
    <section className="sec sec-how" id="how" aria-labelledby="how-title">
      <div className="wrap">
        <header className="sec-head">
          <h2 id="how-title">{h.title}</h2>
          <Rule />
          <p className="sec-lead">{h.lead}</p>
        </header>
        <Frame className="board">
          <div className="board-bar">
            <SegmentedControl value={sc} options={options} onChange={setSc} label={h.pick} className="scen" />
            <p className="board-cap" aria-live="polite">{h.scenarios[sc].caption}</p>
          </div>
          <FlowDiagram
            diagram={diagram}
            {...answerScenarios[sc]}
            label={h.figure}
            stoppedLabel={h.stopped}
            branchLabel={h.branch}
            backLabel={h.back}
            legend={h.legend}
          />
          <MobileFlow diagram={diagram} scenario={answerScenarios[sc]} title={h.pathTitle} others={h.others} ifLabel={h.ifLabel} then={h.then} />
        </Frame>

        <div className="scope">
          <h3 className="sub-title">{h.scopeTitle}</h3>
          <div className="scope-cols">
            {h.scope.map((col, i) => (
              <div className={`scope-col s${i}`} key={col.title}>
                <h4>{col.title}</h4>
                <ul>
                  {col.items.map((it) => (
                    <li key={it}>{it}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <h3 className="sub-title">{h.vsTitle}</h3>
        <p className="sub-lead">{h.vsLead}</p>
        <Frame className="board">
          <FlowDiagram diagram={vs} {...mcpScenario} label={h.vsFigure} stoppedLabel={h.stopped} branchLabel={h.branch} backLabel={h.back} legend={h.vsLegend} />
          <MobileFlow diagram={vs} scenario={mcpScenario} title={h.pathTitle} others={h.others} ifLabel={h.ifLabel} then={h.then} />
        </Frame>
      </div>
    </section>
  );
}

/* ─── Exemples par profil ───────────────────────────────────────────────────────────────────── */
function Examples({ c }: { c: C }) {
  const e = c.examples;
  const [active, setActive] = useState(e.personas[0]!.id);
  const p = e.personas.find((x) => x.id === active) ?? e.personas[0]!;
  const onKey = (ev: KeyboardEvent<HTMLButtonElement>, i: number) => {
    const n = e.personas.length;
    const next = ev.key === "ArrowRight" ? (i + 1) % n : ev.key === "ArrowLeft" ? (i - 1 + n) % n : ev.key === "Home" ? 0 : ev.key === "End" ? n - 1 : -1;
    if (next < 0) return;
    ev.preventDefault();
    setActive(e.personas[next]!.id);
    document.getElementById(`tab-${e.personas[next]!.id}`)?.focus();
  };
  return (
    <section className="sec sec-examples" id="examples" aria-labelledby="ex-title">
      <div className="wrap">
        <header className="sec-head">
          <h2 id="ex-title">{e.title}</h2>
          <Rule />
          <p className="sec-lead">{e.lead}</p>
        </header>
        <div className="tabs" role="tablist" aria-label={e.tabsLabel}>
          {e.personas.map((x, i) => (
            <button
              key={x.id}
              id={`tab-${x.id}`}
              role="tab"
              type="button"
              aria-selected={x.id === active}
              aria-controls={`panel-${x.id}`}
              tabIndex={x.id === active ? 0 : -1}
              onClick={() => setActive(x.id)}
              onKeyDown={(ev) => onKey(ev, i)}
            >
              {x.tab}
            </button>
          ))}
        </div>
        <div className="persona" role="tabpanel" id={`panel-${p.id}`} aria-labelledby={`tab-${p.id}`}>
          <div className="persona-copy">
            {p.badge && <p className="badge">{p.badge}</p>}
            <dl>
              <dt>{e.blocker}</dt>
              <dd>{p.blocker}</dd>
              <dt>{e.brings}</dt>
              <dd>{p.brings}</dd>
            </dl>
          </div>
          <div className="persona-answer">
            {p.tip ? (
              <Tooltip key={p.id} tip={p.tip} question={p.question} live replayLabel={c.hero.showAnswer} useLabel={c.hero.use} copyLabel={c.hero.copy} copiedLabel={c.hero.copied} />
            ) : (
              <figure className="tip-wrap">
                <p className="tip-ask">
                  <span className="tip-ask-who">Brannok</span>
                  <span className="tip-ask-text">{p.question}</span>
                </p>
                <div className="reads">
                  <p className="reads-title">{e.reads}</p>
                  <ul>
                    {p.reads?.map((r) => (
                      <li key={r}>{r}</li>
                    ))}
                  </ul>
                </div>
              </figure>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─── Vie privée ────────────────────────────────────────────────────────────────────────────── */
function Privacy({ c, lang }: { c: C; lang: Lang }) {
  const v = c.privacy;
  const diagram = useMemo(() => localDiagram(lang), [lang]);
  return (
    <section className="sec sec-privacy" id="privacy" aria-labelledby="privacy-title">
      <div className="wrap">
        <header className="sec-head">
          <h2 id="privacy-title">{v.title}</h2>
          <Rule />
          <p className="sec-lead">{v.lead}</p>
        </header>
        <Frame className="board">
          <FlowDiagram diagram={diagram} {...localScenario} label={v.figure} stoppedLabel={c.how.stopped} branchLabel={c.how.branch} backLabel={c.how.back} legend={v.legend} />
          <MobileFlow diagram={diagram} scenario={localScenario} title={c.how.pathTitle} others={c.how.others} ifLabel={c.how.ifLabel} then={c.how.then} />
        </Frame>
        <ul className="vows">
          {v.points.map((p) => (
            <li key={p.title}>
              <h3>{p.title}</h3>
              <p>{p.text}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

/* ─── Installation ──────────────────────────────────────────────────────────────────────────── */
function Install({ c, os, setOs }: { c: C; os: Os; setOs: (o: Os) => void }) {
  const i = c.install;
  const options: Array<SegOption<Os>> = (["mac", "win", "linux"] as const).map((id) => ({ id, label: i.os[id] }));
  const steps: StepDef[] = i.steps[os].map((s, n) => ({ id: `${os}-${n}`, label: s.t, description: s.d, status: n === 0 ? "current" : "upcoming" }));
  const line = os === "win" ? ONE_LINER.win : ONE_LINER.unix;
  return (
    <section className="sec sec-install" id="install" aria-labelledby="install-title">
      <div className="wrap">
        <header className="sec-head">
          <h2 id="install-title">{i.title}</h2>
          <Rule />
          <p className="sec-lead">{i.lead}</p>
        </header>
        <Frame className="forge">
          <div className="forge-os">
            <SegmentedControl value={os} options={options} onChange={setOs} label={i.osLabel} className="os" />
          </div>
          <div className="forge-grid">
            <div className="forge-main">
              <div className="forge-needs">
                <p className="forge-needs-title">{i.needsTitle}</p>
                <ul>
                  {i.needs.map((n) => (
                    <li key={n.text}>
                      {n.href ? <a href={n.href}>{n.text}</a> : n.text}
                      {n.note ? <span className="forge-needs-note"> ({n.note})</span> : null}
                    </li>
                  ))}
                </ul>
                <p className="forge-checks">{i.checks}</p>
              </div>
              {os !== "linux" ? (
                <a className="btn btn-gold btn-lg" href={DL[os]}>
                  <OsIcon os={os} />
                  <span>
                    {osText(i.download[os])}
                    <small>{i.zip[os]}</small>
                  </span>
                </a>
              ) : (
                <p className="forge-linux">{i.linuxOnly}</p>
              )}
              <p className="forge-or">{os === "linux" ? i.inTerminal : os === "win" ? i.orPowershell : i.orTerminal}</p>
              <CopyLine text={line} copy={c.hero.copy} copied={c.hero.copied} />
              <div className="forge-warn">
                <p>{i.warn[os]}</p>
                {os === "mac" && (
                  <p className="forge-geek">
                    {i.geek} <code>{i.geekCmd}</code>
                  </p>
                )}
              </div>
            </div>
            <div className="forge-steps">
              <Stepper steps={steps} orientation="vertical" label={i.stepsLabel} statusLabels={i.status} />
            </div>
          </div>
          <p className="forge-manual">
            <a href={`${REPO}#full-setup`}>{i.manual}</a>
          </p>
        </Frame>
      </div>
    </section>
  );
}

function CopyLine({ text, copy, copied }: { text: string; copy: string; copied: string }) {
  const [done, setDone] = useState(false);
  return (
    <div className="cmd">
      <code tabIndex={0}>{text}</code>
      <button
        type="button"
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(text);
            setDone(true);
            window.setTimeout(() => setDone(false), 1600);
          } catch {
            /* sélection manuelle possible */
          }
        }}
      >
        <span aria-live="polite">{done ? copied : copy}</span>
      </button>
    </div>
  );
}

/* ─── Compatibilité ─────────────────────────────────────────────────────────────────────────── */
function Compat({ c }: { c: C }) {
  const k = c.compat;
  return (
    <section className="sec sec-compat" aria-labelledby="compat-title">
      <div className="wrap narrow">
        <header className="sec-head">
          <h2 id="compat-title">{k.title}</h2>
          <Rule />
          <p className="sec-lead">{k.lead}</p>
        </header>
        <ul className="compat">
          {k.rows.map(([name, models, status], n) => (
            <li key={name} className={n === 0 ? "ok" : n === k.rows.length - 1 ? "no" : "maybe"}>
              <span className="compat-name">{name}</span>
              <span className="compat-models">{models}</span>
              <span className="compat-status">{status}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

/* ─── FAQ ───────────────────────────────────────────────────────────────────────────────────── */
function Faq({ c }: { c: C }) {
  return (
    <section className="sec sec-faq" id="faq" aria-labelledby="faq-title">
      <div className="wrap narrow">
        <header className="sec-head">
          <h2 id="faq-title">{c.faq.title}</h2>
          <Rule />
        </header>
        <div className="faq">
          {c.faq.items.map((f) => (
            <details key={f.q}>
              <summary>{f.q}</summary>
              <p>{f.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── Registre du comparatif : jauges d'encre et tampons ───────────────────────────────── */
const GAUGE_ROWS = new Set([0, 1]); // lignes notées sur 12
const STAMP_ROWS = new Set([3, 4]); // pièges et inventions : 0 pour le compagnon

function Ledger({ k }: { k: C["compare"] }) {
  const ref = useRef<HTMLDivElement>(null);
  const [inked, setInked] = useState(false);
  useEffect(() => {
    const el = ref.current;
    const still = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (!el || still || typeof IntersectionObserver === "undefined") {
      setInked(true);
      return;
    }
    const io = new IntersectionObserver(
      ([e]) => {
        if (e?.isIntersecting) {
          setInked(true);
          io.disconnect();
        }
      },
      { threshold: 0.35 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const cell = (text: string, row: number, col: number) => {
    const nums = GAUGE_ROWS.has(row) ? (text.match(/\d+(?:[.,]\d+)?/g) ?? []).map((n) => parseFloat(n.replace(",", "."))) : [];
    const stamp = col === 1 && STAMP_ROWS.has(row);
    return (
      <>
        {stamp ? <span className="stamp">{text}</span> : text}
        {nums.length > 0 && (
          <span className="gauges" aria-hidden="true">
            {nums.map((n, j) => (
              <span key={j} className={`gauge${nums.length > 1 && j === 0 ? " faint" : ""}`} style={{ "--w": `${(n / 12) * 100}%` } as CSSProperties} />
            ))}
          </span>
        )}
      </>
    );
  };

  return (
    <Frame className={`ledger${inked ? " inked" : ""}`}>
      <div ref={ref} className="ledger-scroll" tabIndex={0} role="region" aria-labelledby="ledger-cap">
        <table>
          <caption id="ledger-cap">{k.caption}</caption>
          <thead>
            <tr>
              {k.cols.map((h, i) => (
                <th key={i} scope="col" className={i === 1 ? "us" : undefined}>
                  {h}
                  {k.sub[i] ? <small>{k.sub[i]}</small> : null}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {k.rows.map(([label, us, gpt, gem], row) => (
              <tr key={label}>
                <th scope="row">{label}</th>
                <td className="us" data-label={k.cols[1]}>{cell(us ?? "", row, 1)}</td>
                <td data-label={k.cols[2]}>{cell(gpt ?? "", row, 2)}</td>
                <td data-label={k.cols[3]}>{cell(gem ?? "", row, 3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="ledger-key">{k.key}</p>
      </div>
      <p className="ledger-note">{k.note}</p>
    </Frame>
  );
}

/** Sceau de cire dessiné pour ce site : goutte irrégulière, anneau et étoile du sceau du projet. */

/* ─── Captures en jeu (fournies par le mainteneur ; absentes, la section ne s'affiche pas) ───── */
function Captures({ c }: { c: C }) {
  const k = c.captures;
  const files = new Map(__CAPTURES__.map((f) => [f.replace(/\.[^.]+$/, ""), f]));
  const shown = k.items.flatMap((it) => {
    const f = files.get(it.file);
    return f ? [{ ...it, src: `${import.meta.env.BASE_URL}captures/${f}` }] : [];
  });
  if (shown.length === 0) return null;
  return (
    <section className="sec sec-captures" id="captures" aria-labelledby="cap-title">
      <div className="wrap">
        <header className="sec-head">
          <h2 id="cap-title">{k.title}</h2>
          <Rule />
          <p className="sec-lead">{k.lead}</p>
        </header>
        <div className="captures">
          {shown.map((it) => (
            <figure className="capture" key={it.file}>
              <img src={it.src} alt={it.alt} loading="lazy" decoding="async" />
              <figcaption>{it.caption}</figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── Appel final ───────────────────────────────────────────────────────────────────────────── */
function Final({ c }: { c: C }) {
  const f = c.final;
  return (
    <section className="sec sec-final" aria-labelledby="final-title">
      <div className="wrap final-in">
        <h2 id="final-title">{f.title}</h2>
        <p className="sec-lead">{f.lead}</p>
        <div className="final-cta">
          <a className="btn btn-gold" href={DL.mac}>
            <OsIcon os="mac" />
            <span>{osText(c.install.download.mac)}</span>
          </a>
          <a className="btn btn-gold" href={DL.win}>
            <OsIcon os="win" />
            {c.install.download.win}
          </a>
          <a className="btn btn-ghost" href="#install">
            <OsIcon os="linux" />
            {f.linux}
          </a>
        </div>
      </div>
    </section>
  );
}

function CopyPageLink({ label, done }: { label: string; done: string }) {
  const [ok, setOk] = useState(false);
  return (
    <button
      type="button"
      className="btn btn-ghost"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(location.href.split("#")[0]!);
          setOk(true);
          window.setTimeout(() => setOk(false), 1800);
        } catch {
          /* le lien reste dans la barre d'adresse */
        }
      }}
    >
      <span aria-live="polite">{ok ? done : label}</span>
    </button>
  );
}
