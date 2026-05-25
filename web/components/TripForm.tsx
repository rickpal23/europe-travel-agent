"use client";

import { useState } from "react";
import type { PlanRequest, Travelers, Wallet } from "@/types";
import { DestinationPicker } from "@/components/DestinationPicker";

const STYLE_OPTIONS = [
  {
    value: "relaxed",
    label: "Relaxed",
    description: "Fewer cities, slower pace, easier with kids",
  },
  {
    value: "balanced",
    label: "Balanced",
    description: "Mix of sightseeing and downtime",
  },
  {
    value: "packed",
    label: "Packed",
    description: "More destinations, faster-moving itinerary",
  },
];

interface Props {
  origin: string;
  travelers: Travelers;
  wallet: Wallet;
  onSubmit: (req: PlanRequest) => void;
  loading: boolean;
}

export function TripForm({ origin, travelers, wallet, onSubmit, loading }: Props) {
  const [required, setRequired] = useState<string[]>(["London", "Paris"]);
  const [optional, setOptional] = useState<string[]>(["Amsterdam", "Rome"]);
  const [style, setStyle] = useState("balanced");
  const [year, setYear] = useState(2026);
  const [minDays, setMinDays] = useState(7);
  const [maxDays, setMaxDays] = useState(10);

  function addCity(city: string) {
    setRequired(prev => [...prev, city]);
  }

  function cycleChip(city: string) {
    if (required.includes(city)) {
      setRequired(prev => prev.filter(c => c !== city));
      setOptional(prev => [...prev, city]);
    } else {
      setOptional(prev => prev.filter(c => c !== city));
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      origin,
      travelers,
      points: wallet,
      required_cities: required,
      optional_cities: optional,
      trip_style: style,
      year,
      min_days: minDays,
      max_days: maxDays,
    });
  }

  const inputCls =
    "w-full rounded-xl border border-zinc-200 bg-white px-3 py-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400";

  return (
    <form onSubmit={handleSubmit} className="space-y-6">

      {/* ── Destinations ─────────────────────────────────────── */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-3">
          Destinations
        </p>
        <DestinationPicker
          required={required}
          optional={optional}
          onAdd={addCity}
          onCycle={cycleChip}
        />
      </div>

      {/* ── Travel style ──────────────────────────────────────── */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-3">
          Travel Style
        </p>
        <div className="flex gap-3">
          {STYLE_OPTIONS.map(opt => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setStyle(opt.value)}
              className={`flex-1 py-3 px-2.5 rounded-xl text-left transition-colors ${
                style === opt.value
                  ? "bg-zinc-900 text-white"
                  : "bg-white border border-zinc-200 text-zinc-700 hover:border-zinc-400"
              }`}
            >
              <p className="text-sm font-semibold leading-snug mb-1">{opt.label}</p>
              <p
                className={`text-xs leading-snug ${
                  style === opt.value ? "text-zinc-400" : "text-zinc-500"
                }`}
              >
                {opt.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* ── When ─────────────────────────────────────────────── */}
      <div className="flex gap-4 items-end">
        <div className="flex-1">
          <label className="text-xs font-semibold uppercase tracking-widest text-zinc-500 block mb-2">
            Year
          </label>
          <input
            type="number"
            value={year}
            min={2025}
            max={2030}
            onChange={e => setYear(Number(e.target.value))}
            className={inputCls}
          />
        </div>
        <div className="flex-1">
          <label className="text-xs font-semibold uppercase tracking-widest text-zinc-500 block mb-2">
            Min days
          </label>
          <input
            type="number"
            value={minDays}
            min={3}
            max={30}
            onChange={e => setMinDays(Number(e.target.value))}
            className={inputCls}
          />
        </div>
        <div className="flex-1">
          <label className="text-xs font-semibold uppercase tracking-widest text-zinc-500 block mb-2">
            Max days
          </label>
          <input
            type="number"
            value={maxDays}
            min={3}
            max={30}
            onChange={e => setMaxDays(Number(e.target.value))}
            className={inputCls}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || required.length === 0}
        className="w-full py-4 rounded-2xl bg-zinc-900 text-white text-base font-semibold tracking-tight transition-opacity hover:opacity-80 disabled:opacity-40"
      >
        {loading ? "Planning your trip…" : "Find my best itinerary →"}
      </button>
    </form>
  );
}
