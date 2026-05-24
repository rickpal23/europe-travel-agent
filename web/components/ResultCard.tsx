import type { Itinerary } from "@/types";

const LIKELIHOOD_COLOR: Record<string, string> = {
  High: "bg-emerald-100 text-emerald-800",
  Medium: "bg-amber-100 text-amber-800",
  Low: "bg-red-100 text-red-800",
};

export function ResultCard({ itinerary, rank }: { itinerary: Itinerary; rank: number }) {
  const { name, stops, score, total_cash, award_likelihood, dates, nights, pros, cons, award_availability } = itinerary;

  return (
    <div className="rounded-2xl bg-white border border-zinc-200 p-6 shadow-sm space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs text-zinc-400 mb-1">#{rank} · Score {score.toFixed(1)}</p>
          <h3 className="text-lg font-semibold text-zinc-900">{name}</h3>
          <p className="text-sm text-zinc-500 mt-0.5">{dates.label} · {nights} nights</p>
        </div>
        <span className={`shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full ${LIKELIHOOD_COLOR[award_likelihood] ?? "bg-zinc-100 text-zinc-600"}`}>
          {award_likelihood} award odds
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {stops.map(([city, nights]: [string, number]) => (
          <span key={city} className="inline-flex items-center gap-1 bg-zinc-100 text-zinc-700 text-xs px-2.5 py-1 rounded-full">
            {city} <span className="text-zinc-400">{nights}n</span>
          </span>
        ))}
      </div>

      <div className="flex gap-6 text-sm">
        <div>
          <p className="text-zinc-400 text-xs">Est. cash value</p>
          <p className="font-semibold text-zinc-900">${total_cash.toLocaleString()}</p>
        </div>
        {award_availability && (
          <div>
            <p className="text-zinc-400 text-xs">Award seats</p>
            <p className="font-semibold text-zinc-900">
              {award_availability.available ? `${award_availability.seat_count} avail` : "Not found"}
            </p>
          </div>
        )}
      </div>

      {(pros.length > 0 || cons.length > 0) && (
        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-zinc-100 text-sm">
          {pros.length > 0 && (
            <ul className="space-y-1">
              {pros.slice(0, 3).map((p, i) => (
                <li key={i} className="text-emerald-700">+ {p}</li>
              ))}
            </ul>
          )}
          {cons.length > 0 && (
            <ul className="space-y-1">
              {cons.slice(0, 3).map((c, i) => (
                <li key={i} className="text-red-600">− {c}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
