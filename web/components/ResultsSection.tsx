import type { Itinerary } from "@/types";
import { WinnerHero } from "./WinnerHero";
import { ItineraryTile } from "./ItineraryTile";

function EmptyState() {
  return (
    <div className="rounded-2xl bg-white border border-zinc-200 shadow-sm px-6 py-8 space-y-5 fade-up">
      {/* Icon treatment */}
      <div className="flex items-center justify-center">
        <div className="w-14 h-14 rounded-full bg-zinc-100 flex items-center justify-center text-2xl">
          ✦
        </div>
      </div>

      {/* Message */}
      <div className="text-center space-y-2">
        <p className="text-base font-semibold text-zinc-900">
          No itineraries found
        </p>
        <p className="text-sm text-zinc-500 leading-relaxed max-w-xs mx-auto">
          The planner couldn&apos;t build a trip from your current selections.
          A few small changes usually fix this.
        </p>
      </div>

      {/* Recovery tips */}
      <div className="rounded-xl bg-zinc-50 border border-zinc-100 px-4 py-4 space-y-2">
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
          Suggestions
        </p>
        <ul className="space-y-1.5">
          {[
            "Add London or Paris as a required stop",
            "Broaden your travel window — try 9 to 14 days",
            "Add more optional destinations for flexibility",
            "Stick to supported cities: Amsterdam, Barcelona, London, Paris, Rome",
          ].map((tip) => (
            <li
              key={tip}
              className="flex items-start gap-2 text-sm text-zinc-600"
            >
              <span className="text-zinc-300 shrink-0 mt-0.5">→</span>
              {tip}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export function ResultsSection({ ranked }: { ranked: Itinerary[] }) {
  if (ranked.length === 0) {
    return <EmptyState />;
  }

  const alternatives = ranked.slice(1);

  return (
    <section className="space-y-4">
      <WinnerHero itinerary={ranked[0]} />

      {alternatives.length > 0 && (
        <div className="space-y-3 pt-2">
          <div className="flex items-baseline gap-2">
            <h2 className="text-lg font-semibold text-zinc-900">
              Other good options
            </h2>
            <span className="text-sm text-zinc-500">
              {alternatives.length} alternative{alternatives.length !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="space-y-3">
            {alternatives.map((it, i) => (
              <ItineraryTile key={i} itinerary={it} rank={i + 2} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
