"use client";

import { useEffect, useState } from "react";
import { getProfile, runPlan } from "@/lib/api";
import type { Profile, PlanRequest, PlanResponse } from "@/types";
import { ProfileCard } from "@/components/ProfileCard";
import { WalletCard } from "@/components/WalletCard";
import { TripForm } from "@/components/TripForm";
import { ResultCard } from "@/components/ResultCard";

export default function Home() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [results, setResults] = useState<PlanResponse | null>(null);
  const [planError, setPlanError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getProfile()
      .then(setProfile)
      .catch((e) => setProfileError(e.message));
  }, []);

  async function handlePlan(req: PlanRequest) {
    setLoading(true);
    setPlanError(null);
    setResults(null);
    try {
      const res = await runPlan(req);
      setResults(res);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e: unknown) {
      setPlanError(e instanceof Error ? e.message : "Planning failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      <div className="max-w-2xl mx-auto px-4 py-12 space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
            Europe Trip Planner
          </h1>
          <p className="mt-1 text-zinc-500 text-sm">
            Plan your itinerary and redeem points for maximum value.
          </p>
        </div>

        {/* Profile + Wallet */}
        {profileError && (
          <div className="rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
            Could not load profile: {profileError}. Make sure the API is running on port 8000.
          </div>
        )}
        {profile && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <ProfileCard profile={profile} />
            <WalletCard wallet={profile.wallet} />
          </div>
        )}

        {/* Results */}
        {results && results.ranked.length > 0 && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-zinc-900">
              {results.ranked.length} itinerar{results.ranked.length === 1 ? "y" : "ies"} found
            </h2>
            {results.ranked.map((itinerary, i) => (
              <ResultCard key={i} itinerary={itinerary} rank={i + 1} />
            ))}
          </section>
        )}
        {results && results.ranked.length === 0 && (
          <div className="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700">
            No itineraries found for these constraints. Try relaxing the city list or duration.
          </div>
        )}

        {/* Plan error */}
        {planError && (
          <div className="rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
            {planError}
          </div>
        )}

        {/* Trip Form */}
        <section className="rounded-2xl bg-white border border-zinc-200 p-6 shadow-sm">
          <h2 className="text-base font-semibold text-zinc-900 mb-6">
            {results ? "Plan another trip" : "Plan your trip"}
          </h2>
          {profile ? (
            <TripForm
              origin={profile.origin}
              travelers={profile.travelers}
              wallet={profile.wallet}
              onSubmit={handlePlan}
              loading={loading}
            />
          ) : !profileError ? (
            <p className="text-sm text-zinc-400">Loading profile…</p>
          ) : null}
        </section>
      </div>
    </div>
  );
}
