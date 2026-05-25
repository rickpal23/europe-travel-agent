"use client";

import { useState, useEffect } from "react";
import type { Itinerary } from "@/types";

// ─── helpers ─────────────────────────────────────────────────────────────────

function fmtPts(n: number | null | undefined): string {
  if (n == null) return "—";
  return n >= 1000 ? `${Math.round(n / 1000)}k` : String(n);
}

function fmtDate(iso: string): string {
  const d = new Date(iso + "T12:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function parseHotelName(line: string): string {
  const after = line.split(" — ")[1] ?? "";
  const parenIdx = after.indexOf(" (");
  return parenIdx > 0 ? after.slice(0, parenIdx) : after;
}

// ─── Score ring ───────────────────────────────────────────────────────────────

function ScoreRing({ score }: { score: number }) {
  const [filled, setFilled] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setFilled(true), 150);
    return () => clearTimeout(t);
  }, []);

  const size = 50;
  const sw = 3.5;
  const r = (size - sw) / 2;
  const circ = 2 * Math.PI * r;
  const offset = filled ? circ - (score / 100) * circ : circ;

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        style={{ transform: "rotate(-90deg)" }}
        aria-hidden
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(0,0,0,0.07)"
          strokeWidth={sw}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#18181b"
          strokeWidth={sw}
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          style={{
            transition: "stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center leading-none gap-0.5">
        <span className="text-base font-bold text-zinc-900">
          {Math.round(score)}
        </span>
        <span className="text-[9px] text-zinc-400">/100</span>
      </div>
    </div>
  );
}

// ─── Pill components ─────────────────────────────────────────────────────────

function StatPill({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center text-sm px-2.5 py-1 rounded-full bg-zinc-100 text-zinc-700 font-medium">
      {children}
    </span>
  );
}

const ODDS_PILL: Record<string, string> = {
  High: "bg-emerald-50 text-emerald-700",
  Medium: "bg-amber-50 text-amber-700",
  Low: "bg-red-50 text-red-700",
};

function OddsPill({ odds }: { odds: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-sm px-2.5 py-1 rounded-full font-medium ${
        ODDS_PILL[odds] ?? "bg-zinc-100 text-zinc-700"
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          odds === "High"
            ? "bg-emerald-500"
            : odds === "Medium"
            ? "bg-amber-500"
            : "bg-red-500"
        }`}
      />
      {odds} odds
    </span>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

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
    moves,
    award_likelihood,
    dates,
    pros,
    cons,
    flight_plan,
    hotel_plan,
    award_availability,
    award_availability_return,
  } = itinerary;

  const totalPts =
    (flight_plan?.amex_used ?? 0) + (hotel_plan?.points_used ?? 0);

  return (
    <div className="rounded-2xl bg-white border border-zinc-200 shadow-sm overflow-hidden">
      {/* Collapsed card — tap to expand */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left p-4 space-y-3 hover:bg-zinc-50/60 transition-colors"
      >
        {/* Row 1: rank + name + score */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0">
            <span className="shrink-0 w-7 h-7 rounded-full bg-zinc-100 text-zinc-700 text-xs font-bold flex items-center justify-center mt-0.5">
              {rank}
            </span>
            <p className="font-semibold text-zinc-900 leading-snug mt-0.5">
              {name}
            </p>
          </div>
          <div className="shrink-0 flex items-center gap-1.5">
            <ScoreRing score={score} />
            <span className="text-zinc-400 text-[10px]">
              {expanded ? "▲" : "▼"}
            </span>
          </div>
        </div>

        {/* Row 2: key trip facts */}
        <p className="text-sm text-zinc-600 pl-10">
          {nights} nights &middot;{" "}
          {dates.depart_day.slice(0, 3)} {fmtDate(dates.depart)} &middot;{" "}
          {moves} hotel change{moves !== 1 ? "s" : ""}
        </p>

        {/* Row 3: stat pills */}
        <div className="flex flex-wrap gap-2 pl-10">
          <StatPill>${total_cash.toLocaleString()} cash</StatPill>
          {totalPts > 0 && (
            <StatPill>{fmtPts(totalPts)} pts total</StatPill>
          )}
          <OddsPill odds={award_likelihood} />
        </div>

        {/* Row 4: one-sentence differentiator */}
        {pros[0] && (
          <p className="text-sm text-zinc-600 pl-10 leading-snug">
            {pros[0]}
          </p>
        )}
      </button>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-zinc-100 px-4 pt-5 pb-5 space-y-5">
          {/* Route */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-2">
              Route
            </p>
            <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
              {stops.map(([city, n], i) => (
                <span key={city} className="flex items-center gap-1.5 text-sm">
                  <span className="font-medium text-zinc-900">{city}</span>
                  <span className="text-zinc-500 text-xs">{n}n</span>
                  {i < stops.length - 1 && (
                    <span className="text-zinc-400 text-xs">→</span>
                  )}
                </span>
              ))}
            </div>
            <p className="text-sm text-zinc-500 mt-1.5">{dates.label}</p>
          </div>

          {/* Flights */}
          {flight_plan && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
                  Flights
                </p>
                {/* Source badges for outbound/return */}
                <div className="flex gap-1.5">
                  {award_availability && (
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        award_availability.source === "seats.aero"
                          ? "bg-emerald-50 text-emerald-600"
                          : "bg-zinc-100 text-zinc-500"
                      }`}
                    >
                      {award_availability.source === "seats.aero" ? "Live" : "Est."}
                    </span>
                  )}
                </div>
              </div>
              <ul className="space-y-1.5">
                <li className="text-sm text-zinc-700">{flight_plan.outbound}</li>
                <li className="text-sm text-zinc-700">{flight_plan.return}</li>
                {flight_plan.intra_cash > 0 && (
                  <li className="text-sm text-zinc-600">
                    In-destination transit: ~$
                    {flight_plan.intra_cash.toLocaleString()}
                  </li>
                )}
                {flight_plan.amex_short > 0 && (
                  <li className="text-sm text-amber-600">
                    Short by {fmtPts(flight_plan.amex_short)} MR pts
                  </li>
                )}
                {/* Award availability summary */}
                {award_availability?.available && (
                  <li className="text-xs text-zinc-500 pt-0.5">
                    Outbound: {award_availability.seat_count} date{award_availability.seat_count !== 1 ? "s" : ""} with space via {award_availability.program}
                    {award_availability_return?.available
                      ? ` · Return: ${award_availability_return.seat_count} date${award_availability_return.seat_count !== 1 ? "s" : ""} via ${award_availability_return.program}`
                      : " · Return: no space found"}
                  </li>
                )}
              </ul>
            </div>
          )}

          {/* Hotels */}
          {hotel_plan && hotel_plan.lines.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-2">
                Hotels
              </p>
              <ul className="space-y-2">
                {hotel_plan.lines.map((line, i) => {
                  const parts = line.split(" — ");
                  const cityNights = parts[0] ?? "";
                  const hotelName = parseHotelName(line);
                  const payment = parts[2] ?? "";
                  return (
                    <li key={i} className="text-sm">
                      <span className="text-zinc-500">{cityNights} · </span>
                      <span className="text-zinc-900 font-medium">{hotelName}</span>
                      {payment && (
                        <span className="text-zinc-600"> · {payment}</span>
                      )}
                    </li>
                  );
                })}
              </ul>
              {hotel_plan.small_room_count > 0 && (
                <p className="text-sm text-amber-600 mt-2">
                  {hotel_plan.small_room_count} room
                  {hotel_plan.small_room_count > 1 ? "s are" : " is"} under
                  400 sqft
                </p>
              )}
            </div>
          )}

          {/* Points breakdown */}
          {(flight_plan || hotel_plan) && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-2">
                Points used
              </p>
              <div className="space-y-1.5 text-sm">
                {flight_plan && (
                  <div className="flex justify-between">
                    <span className="text-zinc-700">Amex MR (flights)</span>
                    <span className="font-medium text-zinc-900">
                      {fmtPts(flight_plan.amex_used)} pts
                    </span>
                  </div>
                )}
                {hotel_plan && hotel_plan.certs_used > 0 && (
                  <div className="flex justify-between">
                    <span className="text-zinc-700">Bonvoy free-night certs</span>
                    <span className="font-medium text-zinc-900">
                      {hotel_plan.certs_used} cert{hotel_plan.certs_used !== 1 ? "s" : ""}
                    </span>
                  </div>
                )}
                {hotel_plan && hotel_plan.points_used > 0 && (
                  <div className="flex justify-between">
                    <span className="text-zinc-700">Bonvoy pts (hotels)</span>
                    <span className="font-medium text-zinc-900">
                      {fmtPts(hotel_plan.points_used)} pts
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Pros */}
          {pros.length > 0 && (
            <ul className="space-y-1.5">
              {pros.slice(0, 4).map((p, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2 text-sm text-zinc-700"
                >
                  <span className="text-emerald-500 shrink-0 mt-0.5">✓</span>
                  {p}
                </li>
              ))}
            </ul>
          )}

          {/* Cons */}
          {cons.length > 0 && (
            <ul className="space-y-1.5">
              {cons.map((c, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2 text-sm text-zinc-600"
                >
                  <span className="text-zinc-400 shrink-0 mt-0.5">−</span>
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
