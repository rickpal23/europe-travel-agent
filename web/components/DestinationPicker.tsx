"use client";

import { useState } from "react";
import { REGIONS, ALL_DESTINATIONS, type Destination } from "@/lib/destinations";

interface Props {
  required: string[];
  optional: string[];
  onAdd: (city: string) => void;
  onCycle: (city: string) => void;
}

// Lookup plannerReady by name for chip rendering
const READY_SET = new Set(
  ALL_DESTINATIONS.filter(d => d.plannerReady).map(d => d.name)
);

export function DestinationPicker({ required, optional, onAdd, onCycle }: Props) {
  const [search, setSearch] = useState("");
  const [regionId, setRegionId] = useState("europe");

  const selectedSet = new Set([...required, ...optional]);
  const q = search.trim().toLowerCase();

  // ── Search: match name or country, exclude already-selected ──────────────
  const searchResults: Destination[] = q.length > 0
    ? ALL_DESTINATIONS.filter(
        dest =>
          !selectedSet.has(dest.name) &&
          (dest.name.toLowerCase().includes(q) ||
           dest.country.toLowerCase().includes(q))
      )
    : [];

  // Group search results by regionId → preserve REGIONS order
  const grouped: Record<string, Destination[]> = {};
  for (const dest of searchResults) {
    if (!grouped[dest.regionId]) grouped[dest.regionId] = [];
    grouped[dest.regionId].push(dest);
  }
  const groupOrder = REGIONS.map(r => r.id).filter(id => grouped[id]);

  // ── Browse: current region's unselected destinations ─────────────────────
  const activeRegion = REGIONS.find(r => r.id === regionId)!;
  const browseDests = activeRegion.destinations.filter(
    dest => !selectedSet.has(dest.name)
  );

  // ── Warning: any selected city that the planner can't handle ─────────────
  const unsupported = [...required, ...optional].filter(c => !READY_SET.has(c));

  return (
    <div>
      {/* Region tabs */}
      <div className="flex gap-2 overflow-x-auto pb-0.5 -mx-1 px-1 mb-3">
        {REGIONS.map(r => (
          <button
            key={r.id}
            type="button"
            onClick={() => { setRegionId(r.id); setSearch(""); }}
            className={`shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${
              regionId === r.id && q === ""
                ? "bg-zinc-900 text-white"
                : "bg-white border border-zinc-200 text-zinc-700 hover:border-zinc-400"
            }`}
          >
            {r.label}
          </button>
        ))}
      </div>

      {/* Hint */}
      <p className="text-xs text-zinc-500 mb-3">
        Tap to require · tap chip to make optional · tap optional to remove
      </p>

      {/* Selected chips */}
      {(required.length > 0 || optional.length > 0) && (
        <div className="space-y-2 mb-3">
          {required.length > 0 && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-medium text-zinc-500 w-16 shrink-0">
                Required
              </span>
              {required.map(city => (
                <button
                  key={city}
                  type="button"
                  onClick={() => onCycle(city)}
                  className="px-3 py-1 rounded-full bg-zinc-900 text-white text-sm font-medium hover:bg-zinc-700 transition-colors"
                >
                  {city}
                </button>
              ))}
            </div>
          )}
          {optional.length > 0 && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-medium text-zinc-500 w-16 shrink-0">
                Optional
              </span>
              {optional.map(city => (
                <button
                  key={city}
                  type="button"
                  onClick={() => onCycle(city)}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-zinc-200 text-zinc-800 text-sm font-medium hover:bg-zinc-300 transition-colors"
                >
                  {city}
                  <span className="text-zinc-500 text-xs leading-none">×</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Unsupported-city warning */}
      {unsupported.length > 0 && (
        <div className="mb-3 rounded-xl bg-amber-50 border border-amber-200 px-3 py-2.5">
          <p className="text-xs font-semibold text-amber-800 mb-0.5">
            Planner data coming soon for: {unsupported.join(", ")}
          </p>
          <p className="text-xs text-amber-700">
            Planning currently covers Amsterdam, Barcelona, London, Paris, and Rome.
            Other cities are shown for browsing — full support is being added.
          </p>
        </div>
      )}

      {/* Search input */}
      <div className="relative mb-2">
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search all destinations…"
          className="w-full rounded-xl border border-zinc-200 bg-white px-3 py-2.5 pr-9 text-sm text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400"
        />
        {search && (
          <button
            type="button"
            onClick={() => setSearch("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-700 text-lg leading-none"
            aria-label="Clear search"
          >
            ×
          </button>
        )}
      </div>

      {/* Search results panel */}
      {q.length > 0 ? (
        <div className="rounded-xl border border-zinc-200 bg-white shadow-sm overflow-y-auto max-h-64">
          {searchResults.length > 0 ? (
            groupOrder.map(rId => {
              const regionLabel = REGIONS.find(r => r.id === rId)?.label ?? rId;
              return (
                <div key={rId}>
                  <p className="px-3 pt-2.5 pb-1 text-[10px] font-semibold uppercase tracking-widest text-zinc-400 bg-zinc-50 border-b border-zinc-100">
                    {regionLabel}
                  </p>
                  {grouped[rId].map(dest => (
                    <button
                      key={dest.id}
                      type="button"
                      onClick={() => onAdd(dest.name)}
                      className="w-full flex items-center justify-between px-3 py-2.5 text-left hover:bg-zinc-50 active:bg-zinc-100 transition-colors border-b border-zinc-50 last:border-0"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-sm font-medium text-zinc-900 truncate">
                          {dest.name}
                        </span>
                        {dest.plannerReady && (
                          <span className="shrink-0 text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full">
                            ready
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-zinc-500 ml-2 shrink-0">
                        {dest.country}
                      </span>
                    </button>
                  ))}
                </div>
              );
            })
          ) : (
            <p className="px-3 py-4 text-sm text-zinc-400 text-center">
              No destinations match &ldquo;{search}&rdquo;
            </p>
          )}
        </div>
      ) : (
        /* Browse grid for active region */
        <div className="flex flex-wrap gap-2">
          {browseDests.length > 0 ? (
            browseDests.map(dest => (
              <button
                key={dest.id}
                type="button"
                onClick={() => onAdd(dest.name)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  dest.plannerReady
                    ? "bg-white border border-zinc-300 text-zinc-800 hover:border-zinc-500"
                    : "bg-white border border-zinc-200 text-zinc-500 hover:border-zinc-400"
                }`}
              >
                {dest.name}
              </button>
            ))
          ) : (
            <p className="text-sm text-zinc-400">
              All {activeRegion.label} cities added.
            </p>
          )}
        </div>
      )}

      {/* Legend */}
      <p className="mt-2 text-[11px] text-zinc-400">
        Darker border = full planner data available
      </p>
    </div>
  );
}
