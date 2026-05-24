"use client";

import { useState } from "react";
import type { Itinerary } from "@/types";

const ODDS_COLOR: Record<string, string> = {
  High: "text-emerald-600",
  Medium: "text-amber-600",
  Low: "text-red-600",
};

function parseHotelName(line: string): string {
  const after = line.split(" — ")[1] ?? "";
  const parenIdx = after.indexOf(" (");
  return parenIdx > 0 ? after.slice(0, parenIdx) : after;
}

export function ItineraryTile({
  itinerary,
  rank,
}: {
  itinerary: Itinerary;
  rank: number;
}) {
  const [expanded, setExpanded] = useState(false);

  const {
    name,
    stops,
    score,
    total_cash,
    nights,
    award_likelihood,
    dates,
    pros,
    cons,
    flight_plan,
    hotel_plan,
  } = itinerary;

  return (
    <div className="rounded-2xl bg-white border border-zinc-200 shadow-sm overflow-hidden">
      {/* Summary row — tap to expand */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left px-4 py-4 flex items-start justify-between gap-4 hover:bg-zinc-50/70 transition-colors"
      >
        <div className="flex items-start gap-3 min-w-0">
          <span className="shrink-0 w-7 h-7 rounded-full bg-zinc-100 text-zinc-500 text-xs font-semibold flex items-center justify-center">
            {rank}
          </span>
          <div className="min-w-0">
            <p className="font-semibold text-zinc-900 text-sm leading-snug truncate">
              {name}
            </p>
            <p className="text-xs text-zinc-400 mt-0.5">
              {nights}n &middot; ${total_cash.toLocaleString()} &middot;{" "}
              <span className={ODDS_COLOR[award_likelihood]}>
                {award_likelihood} odds
              </span>
            </p>
          </div>
        </div>
        <div className="shrink-0 flex items-center gap-2">
          <span className="text-xl font-bold text-zinc-900 leading-none">
            {Math.round(score)}
          </span>
          <span className="text-zinc-300 text-[10px]">
            {expanded ? "▲" : "▼"}
          </span>
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-zinc-100 px-4 pt-4 pb-5 space-y-5">
          {/* Route */}
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-400 mb-2">
              Route
            </p>
            <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1">
              {stops.map(([city, n], i) => (
                <span key={city} className="flex items-center gap-1.5 text-sm">
                  <span className="font-medium text-zinc-900">{city}</span>
                  <span className="text-zinc-400 text-xs">{n}n</span>
                  {i < stops.length - 1 && (
                    <span className="text-zinc-300 text-xs">→</span>
                  )}
                </span>
              ))}
            </div>
            <p className="text-xs text-zinc-400 mt-1.5">{dates.label}</p>
          </div>

          {/* Flights */}
          {flight_plan && (
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-400 mb-2">
                Flights
              </p>
              <ul className="space-y-1.5">
                <li className="text-sm text-zinc-700">{flight_plan.outbound}</li>
                <li className="text-sm text-zinc-700">{flight_plan.return}</li>
                {flight_plan.intra_cash > 0 && (
                  <li className="text-xs text-zinc-400">
                    Intra-Europe transit: ~${flight_plan.intra_cash.toLocaleString()}
                  </li>
                )}
              </ul>
            </div>
          )}

          {/* Hotels */}
          {hotel_plan && hotel_plan.lines.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-400 mb-2">
                Hotels
              </p>
              <ul className="space-y-1.5">
                {hotel_plan.lines.map((line, i) => {
                  const parts = line.split(" — ");
                  const cityNights = parts[0] ?? "";
                  const hotelName = parseHotelName(line);
                  const payment = parts[2] ?? "";
                  return (
                    <li key={i} className="text-sm">
                      <span className="text-zinc-400">{cityNights} · </span>
                      <span className="text-zinc-800 font-medium">{hotelName}</span>
                      {payment && (
                        <span className="text-zinc-400"> · {payment}</span>
                      )}
                    </li>
                  );
                })}
              </ul>
              {hotel_plan.small_room_count > 0 && (
                <p className="text-xs text-amber-600 mt-2">
                  {hotel_plan.small_room_count} room
                  {hotel_plan.small_room_count > 1 ? "s are" : " is"} under
                  400 sqft
                </p>
              )}
            </div>
          )}

          {/* Pros */}
          {pros.length > 0 && (
            <ul className="space-y-1.5">
              {pros.slice(0, 3).map((p, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2 text-sm text-zinc-600"
                >
                  <span className="text-emerald-400 shrink-0 mt-0.5">✓</span>
                  {p}
                </li>
              ))}
            </ul>
          )}

          {/* Cons */}
          {cons.length > 0 && (
            <ul className="space-y-1.5">
              {cons.slice(0, 3).map((c, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2 text-sm text-zinc-400"
                >
                  <span className="text-zinc-300 shrink-0 mt-0.5">−</span>
                  {c}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
