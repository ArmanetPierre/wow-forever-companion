import type { CSSProperties } from "react";

/** Point en coordonnées /way : pourcentage de la carte entière, origine en haut à gauche. */
export interface MapPin {
  x: number;
  y: number;
  /** Numéro ou lettre affiché dans la pastille. */
  n: string;
  /** Décalage de la pastille par rapport au point exact, en px (repères trop proches). */
  dx?: number;
  dy?: number;
}

interface Props {
  /** Image de la carte entière (taille native du client). */
  src: string;
  /** Fenêtre affichée, en % de la carte : x, y, largeur, hauteur. */
  view: [number, number, number, number];
  /** Rapport largeur / hauteur de la carte entière. */
  ratio?: number;
  label: string;
  pins: MapPin[];
  /** Position du joueur (fictive) : point bleu. */
  me?: { x: number; y: number };
  /** Repère mis en avant : halo, chemin depuis le joueur, coordonnées. */
  hot?: number | null;
  className?: string;
  children?: React.ReactNode;
  loading?: "eager" | "lazy";
}

/**
 * Vraie carte de zone (client du jeu), recadrée en CSS : l'image reste celle du client, intacte.
 * Les repères sont des éléments HTML posés en % sur la carte entière, donc exactement aux coordonnées /way.
 */
export function RealMap({ src, view, ratio = 1002 / 668, label, pins, me, hot = null, className, children, loading = "lazy" }: Props) {
  const [vx, vy, vw, vh] = view;
  // La « feuille » a la taille de la carte entière, décalée pour que la fenêtre remplisse le cadre.
  const sheet: CSSProperties = {
    width: `${(100 / vw) * 100}%`,
    height: `${(100 / vh) * 100}%`,
    left: `${(-vx / vw) * 100}%`,
    top: `${(-vy / vh) * 100}%`,
  };
  const frame: CSSProperties = { aspectRatio: `${vw * ratio} / ${vh}` };
  const target = hot != null ? pins[hot] : undefined;
  const at = (x: number, y: number): CSSProperties => ({ left: `${x}%`, top: `${y}%` });

  return (
    <figure className={`rmap${className ? ` ${className}` : ""}`}>
      <div className="rmap-frame" style={frame} role="img" aria-label={label}>
        <div className="rmap-sheet" style={sheet}>
          <img src={src} alt="" width={1002} height={668} loading={loading} decoding="async" draggable={false} />
          {target && me && (
            <svg className="rmap-route" viewBox="0 0 1002 668" aria-hidden="true">
              <path key={hot} pathLength={1} d={`M${me.x * 10.02} ${me.y * 6.68} L${target.x * 10.02} ${target.y * 6.68}`} />
            </svg>
          )}
          {me && <span className="rmap-me" style={at(me.x, me.y)} aria-hidden="true" />}
          {pins.map((p, i) => (
            <span key={i} className={`rmap-pin${hot === i ? " hot" : ""}`} style={at(p.x, p.y)} aria-hidden="true">
              <span className="rmap-dot" />
              {Boolean(p.dx || p.dy) && <span className="rmap-lead" style={{ "--dx": `${p.dx ?? 0}px`, "--dy": `${p.dy ?? 0}px` } as CSSProperties} />}
              <span className="rmap-badge" style={{ transform: `translate(calc(-50% + ${p.dx ?? 0}px), calc(-50% + ${p.dy ?? 0}px))` }}>
                {p.n}
              </span>
              {hot === i && <span className="rmap-coords">{`${p.x.toFixed(1)}, ${p.y.toFixed(1)}`}</span>}
            </span>
          ))}
        </div>
      </div>
      {children}
    </figure>
  );
}
