import { useEffect, useId, useRef, useState, type CSSProperties } from "react";
import type { Tip } from "../content";

interface Props {
  tip: Tip;
  /** Libellé « Utiliser : » des lignes /way. */
  useLabel: string;
  copyLabel: string;
  copiedLabel: string;
  /** Question posée, affichée au-dessus comme une ligne de chat. */
  question?: string;
  /** Nom de celui qui pose la question. */
  who?: string;
  /** La question devient un lien d'objet : au survol, au focus ou au toucher, la réponse se rejoue. */
  live?: boolean;
  /** Texte d'aide du lien (lecteurs d'écran). */
  replayLabel?: string;
  /** Survol d'une ligne « Utiliser » : son rang parmi les lignes /way, ou null en sortie. */
  onWay?: (index: number | null) => void;
  /** Ligne /way mise en avant depuis l'extérieur. */
  hot?: number | null;
  className?: string;
  id?: string;
}

const reduced = () => typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

/** Réponse du compagnon mise en forme comme une infobulle d'objet : nom en couleur de qualité,
 *  lignes « Utiliser : » en vert avec le /way copiable, source et certitude en bas.
 *  En mode `live`, la réponse arrive ligne après ligne à l'entrée dans l'écran, puis se rejoue au survol du lien. */
export function Tooltip({ tip, useLabel, copyLabel, copiedLabel, question, who = "Brannok", live, replayLabel, onWay, hot, className, id }: Props) {
  const [play, setPlay] = useState(0);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!live || reduced() || typeof IntersectionObserver === "undefined") return;
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e?.isIntersecting) {
          setPlay((n) => n + 1);
          io.disconnect();
        }
      },
      { threshold: 0.4 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [live]);

  const replay = () => {
    if (!reduced()) setPlay((n) => n + 1);
  };
  const ask = question ?? (live ? tip.name : undefined);
  const tipId = `tip-${useId().replace(/[^\w-]/g, "")}`;
  let wayIndex = -1;

  return (
    <figure className={`tip-wrap${live ? " live" : ""}${className ? ` ${className}` : ""}`} id={id} ref={ref}>
      {ask && (
        <p className="tip-ask">
          <span className="tip-ask-who">{who}</span>
          {live ? (
            <button
              type="button"
              className={`tip-link q-${tip.quality}`}
              onMouseEnter={replay}
              onFocus={replay}
              onClick={replay}
              aria-describedby={tipId}
              title={replayLabel}
            >
              [{ask}]
            </button>
          ) : (
            <span className="tip-ask-text">{ask}</span>
          )}
        </p>
      )}
      <div key={play} id={tipId} className={`tip q-${tip.quality}${play > 0 ? " arrive" : ""}`}>
        <p className="tip-name" style={{ "--i": 0 } as CSSProperties}>
          {tip.name}
        </p>
        {tip.lines.map((line, i) => {
          const style = { "--i": i + 1 } as CSSProperties;
          if (line.kind !== "use") {
            return (
              <p key={i} className={`tip-${line.kind}`} style={style}>
                {line.text}
              </p>
            );
          }
          wayIndex += 1;
          const n = wayIndex;
          const on = onWay ? () => onWay(n) : undefined;
          const off = onWay ? () => onWay(null) : undefined;
          return (
            <p key={i} className={`tip-use${hot === n ? " hot" : ""}`} style={style} onMouseEnter={on} onMouseLeave={off} onFocus={on} onBlur={off}>
              <span>
                {useLabel} {line.text}
              </span>
              {line.way && <WayChip way={line.way} copy={copyLabel} copied={copiedLabel} />}
            </p>
          );
        })}
      </div>
    </figure>
  );
}

function WayChip({ way, copy, copied }: { way: string; copy: string; copied: string }) {
  const [done, setDone] = useState(false);
  const onClick = async () => {
    try {
      await navigator.clipboard.writeText(way);
      setDone(true);
      window.setTimeout(() => setDone(false), 1600);
    } catch {
      /* presse-papiers refusé : le texte reste sélectionnable */
    }
  };
  return (
    <button type="button" className={`way${done ? " done" : ""}`} onClick={onClick} aria-label={`${copy} ${way}`}>
      <code>{way}</code>
      <span className="way-state" aria-live="polite">
        {done ? copied : ""}
      </span>
    </button>
  );
}
