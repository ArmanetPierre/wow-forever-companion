import type { ReactNode } from "react";

/** Coin orné, dessiné pour ce site : filet doré qui se termine en volute et en losange. */
function Corner({ pos }: { pos: "tl" | "tr" | "bl" | "br" }) {
  return (
    <svg className={`corner ${pos}`} viewBox="0 0 40 40" aria-hidden="true" focusable="false">
      <path d="M1.5 38.5V12.5Q1.5 1.5 12.5 1.5H38.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
      <path d="M6 30V14Q6 6 14 6H30" fill="none" stroke="currentColor" strokeWidth="0.8" opacity="0.6" />
      <path d="M12.5 12.5m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" fill="currentColor" />
      <path d="M1.5 38.5l-1.2 1.2M38.5 1.5l1.2-1.2" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

/** Cadre à coins ornés autour d'un contenu. */
export function Frame({ children, className, as: Tag = "div" }: { children: ReactNode; className?: string; as?: "div" | "section" | "article" | "aside" }) {
  return (
    <Tag className={`frame${className ? ` ${className}` : ""}`}>
      <Corner pos="tl" />
      <Corner pos="tr" />
      <Corner pos="bl" />
      <Corner pos="br" />
      {children}
    </Tag>
  );
}

/** Séparateur : filet doré avec un losange au centre. */
export function Rule() {
  return (
    <svg className="rule" viewBox="0 0 240 14" aria-hidden="true" focusable="false" preserveAspectRatio="xMidYMid meet">
      <path d="M0 7H100M140 7H240" stroke="currentColor" strokeWidth="1" />
      <path d="M120 1l6 6-6 6-6-6z" fill="none" stroke="currentColor" strokeWidth="1.2" />
      <path d="M120 4.5l2.5 2.5-2.5 2.5-2.5-2.5z" fill="currentColor" />
      <circle cx="106" cy="7" r="1.6" fill="currentColor" />
      <circle cx="134" cy="7" r="1.6" fill="currentColor" />
    </svg>
  );
}

/** Sceau du projet : étoile de boussole dans un anneau, dessinée pour ce site. */
export function Sigil({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true" focusable="false" className="sigil">
      <circle cx="32" cy="32" r="29" fill="none" stroke="currentColor" strokeWidth="2.5" />
      <circle cx="32" cy="32" r="23" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.6" />
      <path d="M32 6 L37 27 L58 32 L37 37 L32 58 L27 37 L6 32 L27 27 Z" fill="currentColor" />
      <path d="M32 16 L34.5 29.5 L48 32 L34.5 34.5 L32 48 L29.5 34.5 L16 32 L29.5 29.5 Z" fill="#0d1220" opacity="0.55" />
      <circle cx="32" cy="32" r="3.2" fill="#7fb2ff" />
    </svg>
  );
}

export function GitHubIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <path
        fill="currentColor"
        d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
      />
    </svg>
  );
}

export function OsIcon({ os }: { os: "mac" | "win" | "linux" }) {
  if (os === "win")
    return (
      <svg width="18" height="18" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
        <path fill="currentColor" d="M0 2.2 6.5 1.3v6.2H0zM7.3 1.2 16 0v7.5H7.3zM0 8.3h6.5v6.3L0 13.7zM7.3 8.3H16V16l-8.7-1.2z" />
      </svg>
    );
  if (os === "mac")
    return (
      <svg width="18" height="18" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
        <path
          fill="currentColor"
          d="M11.2 8.5c0-1.7 1.4-2.5 1.5-2.6-.8-1.2-2-1.3-2.5-1.3-1.1-.1-2.1.6-2.6.6-.5 0-1.4-.6-2.3-.6C4.1 4.6 3 5.3 2.4 6.4c-1.3 2.2-.3 5.5.9 7.3.6.9 1.3 1.9 2.2 1.8.9 0 1.2-.6 2.3-.6 1.1 0 1.4.6 2.3.6.9 0 1.6-.9 2.2-1.8.7-1 1-2 1-2.1-.1 0-1.9-.7-1.9-3.1zM9.5 3.4c.5-.6.8-1.4.7-2.2-.7 0-1.5.5-2 1.1-.4.5-.8 1.3-.7 2.1.8.1 1.5-.4 2-1z"
        />
      </svg>
    );
  return (
    <svg width="18" height="18" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <path fill="currentColor" d="M2 2h12v12H2zm1.5 1.5v9h9v-9zM5 5.5l2.5 2-2.5 2-.8-.9L5.8 7.5 4.2 6.4zM8 9.5h3.5v1.2H8z" />
    </svg>
  );
}
