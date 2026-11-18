import type { FlowDiagramDef, FlowScenario } from "@ui-kit";

interface Props {
  diagram: FlowDiagramDef;
  scenario: FlowScenario;
  title: string;
  others: string;
  /** « si non : » : préfixe d'un lien libellé (oui, non…). */
  ifLabel: (label: string) => string;
  /** « puis : » : préfixe d'un lien sans libellé. */
  then: string;
}

const CHOICES = new Set(["oui", "non", "yes", "no"]);

/**
 * Version étroite d'un schéma de flux (sous 900 px, où le canevas d'ui-kit disparaît) :
 * le parcours de l'exemple seul, étape par étape, et les embranchements non pris repliés dans un <details>.
 * Remplace la liste d'ui-kit à cette largeur, qui déroule tout au même niveau.
 */
export function MobileFlow({ diagram, scenario, title, others, ifLabel, then }: Props) {
  const via = (label?: string) => (label ? (CHOICES.has(label) ? ifLabel(label) : label) : undefined);
  const nodes = new Map(diagram.nodes.map((n) => [n.id, n]));
  const edges = new Map(diagram.edges.map((e) => [e.id, e]));
  const hops = scenario.route.flatMap((id) => edges.get(id) ?? []);
  const first = hops[0]?.from;
  const steps = first ? [{ node: first, via: undefined as string | undefined }, ...hops.map((e) => ({ node: e.to, via: e.label }))] : [];
  const onRoute = new Set(scenario.route);
  const visited = new Set(steps.map((s) => s.node));
  const branches = diagram.edges.filter((e) => !onRoute.has(e.id) && visited.has(e.from));

  return (
    <div className="mflow">
      <p className="mflow-title">{title}</p>
      <ol className="mflow-path">
        {steps.map(({ node, via }, i) => {
          const n = nodes.get(node);
          if (!n) return null;
          return (
            <li key={`${node}-${i}`} className={`mflow-step ${n.kind}`}>
              {via && <span className="mflow-via">{CHOICES.has(via) ? ifLabel(via) : via}</span>}
              <span className="mflow-name">{n.label}</span>
              {n.sublabel && <span className="mflow-sub">{n.sublabel}</span>}
            </li>
          );
        })}
      </ol>
      {branches.length > 0 && (
        <details className="mflow-more">
          <summary>
            {others} ({branches.length})
          </summary>
          <ul>
            {branches.map((e) => (
              <li key={e.id}>
                <span className="mflow-from">{nodes.get(e.from)?.label}</span>{" "}
                <span className="mflow-via">{via(e.label) ?? then}</span> {nodes.get(e.to)?.label}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
