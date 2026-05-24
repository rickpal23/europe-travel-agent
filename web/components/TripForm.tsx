"use client";

import { useState } from "react";
import type { PlanRequest, Travelers, Wallet } from "@/types";

const CITY_OPTIONS = [
  "London", "Paris", "Rome", "Barcelona", "Amsterdam",
  "Lisbon", "Prague", "Vienna", "Dublin", "Athens",
  "Copenhagen", "Budapest", "Florence", "Zurich", "Porto",
];

const STYLE_OPTIONS = [
  { value: "relaxed", label: "Relaxed" },
  { value: "balanced", label: "Balanced" },
  { value: "packed", label: "Packed" },
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
  const [optional, setOptional] = useState<string[]>([]);
  const [style, setStyle] = useState("balanced");
  const [year, setYear] = useState(2026);
  const [minDays, setMinDays] = useState(7);
  const [maxDays, setMaxDays] = useState(10);

  function toggleCity(city: string, list: string[], setList: (v: string[]) => void, other: string[], setOther: (v: string[]) => void) {
    if (list.includes(city)) {
      setList(list.filter((c) => c !== city));
    } else {
      setOther(other.filter((c) => c !== city));
      setList([...list, city]);
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

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3">
          Destinations
        </p>
        <p className="text-xs text-zinc-500 mb-2">Required (must visit)</p>
        <div className="flex flex-wrap gap-2 mb-3">
          {CITY_OPTIONS.map((city) => (
            <button
              key={city}
              type="button"
              onClick={() => toggleCity(city, required, setRequired, optional, setOptional)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                required.includes(city)
                  ? "bg-zinc-900 text-white"
                  : "bg-white border border-zinc-200 text-zinc-700 hover:border-zinc-400"
              }`}
            >
              {city}
            </button>
          ))}
        </div>
        <p className="text-xs text-zinc-500 mb-2">Optional (nice to have)</p>
        <div className="flex flex-wrap gap-2">
          {CITY_OPTIONS.map((city) => (
            <button
              key={city}
              type="button"
              onClick={() => toggleCity(city, optional, setOptional, required, setRequired)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                optional.includes(city)
                  ? "bg-zinc-500 text-white"
                  : required.includes(city)
                  ? "opacity-30 cursor-default bg-white border border-zinc-200 text-zinc-700"
                  : "bg-white border border-zinc-200 text-zinc-700 hover:border-zinc-400"
              }`}
              disabled={required.includes(city)}
            >
              {city}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3">
          Travel Style
        </p>
        <div className="flex gap-3">
          {STYLE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setStyle(opt.value)}
              className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                style === opt.value
                  ? "bg-zinc-900 text-white"
                  : "bg-white border border-zinc-200 text-zinc-700 hover:border-zinc-400"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-4 items-end">
        <div className="flex-1">
          <label className="text-xs font-semibold uppercase tracking-widest text-zinc-400 block mb-2">
            Year
          </label>
          <input
            type="number"
            value={year}
            min={2025}
            max={2030}
            onChange={(e) => setYear(Number(e.target.value))}
            className="w-full rounded-xl border border-zinc-200 bg-white px-3 py-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400"
          />
        </div>
        <div className="flex-1">
          <label className="text-xs font-semibold uppercase tracking-widest text-zinc-400 block mb-2">
            Min days
          </label>
          <input
            type="number"
            value={minDays}
            min={3}
            max={30}
            onChange={(e) => setMinDays(Number(e.target.value))}
            className="w-full rounded-xl border border-zinc-200 bg-white px-3 py-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400"
          />
        </div>
        <div className="flex-1">
          <label className="text-xs font-semibold uppercase tracking-widest text-zinc-400 block mb-2">
            Max days
          </label>
          <input
            type="number"
            value={maxDays}
            min={3}
            max={30}
            onChange={(e) => setMaxDays(Number(e.target.value))}
            className="w-full rounded-xl border border-zinc-200 bg-white px-3 py-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400"
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
