"use client";

import { useState } from "react";
import type { Profile, Travelers } from "@/types";

interface Props {
  profile: Profile;
  onSave: (updates: { name: string; origin: string; travelers: Travelers }) => Promise<void>;
}

function Stepper({
  value,
  min,
  max,
  onChange,
}: {
  value: number;
  min: number;
  max: number;
  onChange: (n: number) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={() => onChange(Math.max(min, value - 1))}
        disabled={value <= min}
        className="w-8 h-8 rounded-full border border-zinc-200 text-zinc-700 flex items-center justify-center text-lg leading-none hover:border-zinc-400 transition-colors disabled:opacity-30"
      >
        −
      </button>
      <span className="text-sm font-semibold text-zinc-900 w-5 text-center">
        {value}
      </span>
      <button
        type="button"
        onClick={() => onChange(Math.min(max, value + 1))}
        disabled={value >= max}
        className="w-8 h-8 rounded-full border border-zinc-200 text-zinc-700 flex items-center justify-center text-lg leading-none hover:border-zinc-400 transition-colors disabled:opacity-30"
      >
        +
      </button>
    </div>
  );
}

export function ProfileCard({ profile, onSave }: Props) {
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const [name, setName] = useState(profile.name);
  const [origin, setOrigin] = useState(profile.origin);
  const [adults, setAdults] = useState(profile.travelers.adults);
  const [kids, setKids] = useState(profile.travelers.kids);
  const [kidsAges, setKidsAges] = useState<number[]>(profile.travelers.kids_ages ?? []);

  function openEdit() {
    setName(profile.name);
    setOrigin(profile.origin);
    setAdults(profile.travelers.adults);
    setKids(profile.travelers.kids);
    setKidsAges(profile.travelers.kids_ages ?? []);
    setSaveError(null);
    setEditing(true);
  }

  function handleKidsChange(n: number) {
    setKids(n);
    if (n > kidsAges.length) {
      setKidsAges([...kidsAges, ...Array(n - kidsAges.length).fill(5)]);
    } else {
      setKidsAges(kidsAges.slice(0, n));
    }
  }

  async function handleSave() {
    setSaving(true);
    setSaveError(null);
    try {
      await onSave({
        name: name.trim(),
        origin: origin.toUpperCase().trim().slice(0, 3),
        travelers: { adults, kids, kids_ages: kidsAges },
      });
      setEditing(false);
    } catch (e: unknown) {
      setSaveError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  const inputCls =
    "w-full rounded-xl border border-zinc-200 bg-white px-3 py-2.5 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400";

  const { name: pName, origin: pOrigin, travelers } = profile;
  const travelerLabel =
    travelers.kids > 0
      ? `${travelers.adults} adult${travelers.adults !== 1 ? "s" : ""}, ${travelers.kids} kid${travelers.kids !== 1 ? "s" : ""}`
      : `${travelers.adults} adult${travelers.adults !== 1 ? "s" : ""}`;

  if (editing) {
    return (
      <div className="rounded-2xl bg-white border border-zinc-200 p-5 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-4">
          Traveler
        </p>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={inputCls}
              placeholder="Your name"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">
              Origin airport (IATA code)
            </label>
            <input
              value={origin}
              onChange={(e) => setOrigin(e.target.value.toUpperCase())}
              maxLength={3}
              className={inputCls}
              placeholder="SFO"
            />
          </div>
          <div className="flex gap-6">
            <div>
              <p className="text-xs text-zinc-500 mb-2">Adults</p>
              <Stepper value={adults} min={1} max={8} onChange={setAdults} />
            </div>
            <div>
              <p className="text-xs text-zinc-500 mb-2">Kids</p>
              <Stepper value={kids} min={0} max={6} onChange={handleKidsChange} />
            </div>
          </div>
          {kids > 0 && (
            <div>
              <p className="text-xs text-zinc-500 mb-2">Kid ages</p>
              <div className="flex gap-2 flex-wrap">
                {kidsAges.map((age, i) => (
                  <div key={i} className="text-center">
                    <input
                      type="number"
                      value={age}
                      min={0}
                      max={17}
                      onChange={(e) => {
                        const next = [...kidsAges];
                        next[i] = Number(e.target.value);
                        setKidsAges(next);
                      }}
                      className="w-14 rounded-xl border border-zinc-200 px-2 py-2 text-sm text-center text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400"
                    />
                    <p className="text-[10px] text-zinc-400 mt-0.5">
                      kid {i + 1}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {saveError && (
            <p className="text-xs text-red-600">{saveError}</p>
          )}
          <div className="flex gap-2 pt-1">
            <button
              type="button"
              onClick={() => setEditing(false)}
              className="flex-1 py-2.5 rounded-xl border border-zinc-200 text-sm text-zinc-700 hover:border-zinc-400 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={saving}
              className="flex-1 py-2.5 rounded-xl bg-zinc-900 text-white text-sm font-semibold disabled:opacity-50 hover:opacity-80 transition-opacity"
            >
              {saving ? "Saving…" : "Save"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-white border border-zinc-200 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
          Traveler
        </p>
        <button
          type="button"
          onClick={openEdit}
          className="text-xs font-medium text-zinc-500 hover:text-zinc-900 transition-colors"
        >
          Edit
        </button>
      </div>
      <p className="text-xl font-semibold text-zinc-900">{pName || "—"}</p>
      <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-sm text-zinc-600">
        <span>
          Flying from <strong className="text-zinc-900">{pOrigin}</strong>
        </span>
        <span className="text-zinc-300">·</span>
        <span>{travelerLabel}</span>
      </div>
    </div>
  );
}
