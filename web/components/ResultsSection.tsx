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

  return (
    <section className="space-y-3">
      <WinnerHero itinerary={ranked[0]} />

      {ranked.length > 1 && (
        <>
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-400 px-1 pt-3">
            Alternatives
          </p>
          <div className="space-y-2">
            {ranked.slice(1).map((it, i) => (
              <ItineraryTile key={i} itinerary={it} rank={i + 2} />
            ))}
          </div>
        </>
      )}
    </section>
  );
}
