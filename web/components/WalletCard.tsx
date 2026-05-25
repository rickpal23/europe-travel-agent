"use client";

import { useState } from "react";
import type { Wallet } from "@/types";

interface Props {
  wallet: Wallet;
  onSave: (wallet: Wallet) => Promise<void>;
}

function fmt(n: number) {
  return n >= 1_000_000
    ? `${(n / 1_000_000).toFixed(1)}M`
    : n >= 1000
    ? `${Math.round(n / 1000)}k`
    : String(n);
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="text-lg font-semibold text-zinc-900">{value}</p>
    </div>
  );
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

export function WalletCard({ wallet, onSave }: Props) {
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const [amexMr, setAmexMr] = useState(wallet.amex_mr);
  const [bonvoyPts, setBonvoyPts] = useState(wallet.bonvoy_points);
  const [freeNights, setFreeNights] = useState(wallet.marriott_free_nights);

  function openEdit() {
    setAmexMr(wallet.amex_mr);
    setBonvoyPts(wallet.bonvoy_points);
    setFreeNights(wallet.marriott_free_nights);
    setSaveError(null);
    setEditing(true);
  }

  async function handleSave() {
    setSaving(true);
    setSaveError(null);
    try {
      await onSave({
        amex_mr: amexMr,
        bonvoy_points: bonvoyPts,
        marriott_free_nights: freeNights,
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

  if (editing) {
    return (
      <div className="rounded-2xl bg-white border border-zinc-200 p-5 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-4">
          Points Wallet
        </p>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-zinc-500 block mb-1">
              Amex MR points
            </label>
            <input
              type="number"
              value={amexMr}
              min={0}
              step={1000}
              onChange={(e) => setAmexMr(Number(e.target.value))}
              className={inputCls}
              placeholder="e.g. 200000"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">
              Bonvoy points
            </label>
            <input
              type="number"
              value={bonvoyPts}
              min={0}
              step={1000}
              onChange={(e) => setBonvoyPts(Number(e.target.value))}
              className={inputCls}
              placeholder="e.g. 250000"
            />
          </div>
          <div>
            <p className="text-xs text-zinc-500 mb-2">Free night certs</p>
            <Stepper
              value={freeNights}
              min={0}
              max={10}
              onChange={setFreeNights}
            />
          </div>
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
          Points Wallet
        </p>
        <button
          type="button"
          onClick={openEdit}
          className="text-xs font-medium text-zinc-500 hover:text-zinc-900 transition-colors"
        >
          Edit
        </button>
      </div>
      <div className="flex gap-6 flex-wrap">
        <Stat label="Amex MR" value={fmt(wallet.amex_mr)} />
        <Stat label="Bonvoy pts" value={fmt(wallet.bonvoy_points)} />
        <Stat label="Free nights" value={String(wallet.marriott_free_nights)} />
      </div>
    </div>
  );
}
