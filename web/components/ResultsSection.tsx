import type { Itinerary } from "@/types";
import { WinnerHero } from "./WinnerHero";
import { ItineraryTile } from "./ItineraryTile";

export function ResultsSection({ ranked }: { ranked: Itinerary[] }) {
  if (ranked.length === 0) {
    return (
      <div className="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700">
        No itineraries found. Try relaxing the city list or duration range.
      </div>
    );
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
