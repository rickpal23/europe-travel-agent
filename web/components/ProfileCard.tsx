import type { Profile } from "@/types";

export function ProfileCard({ profile }: { profile: Profile }) {
  const { name, origin, travelers } = profile;
  const travelerLabel =
    travelers.adults === 1 && travelers.kids === 0
      ? "1 adult"
      : travelers.kids > 0
      ? `${travelers.adults} adults, ${travelers.kids} kid${travelers.kids > 1 ? "s" : ""}`
      : `${travelers.adults} adults`;

  return (
    <div className="rounded-2xl bg-white border border-zinc-200 p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3">
        Traveler
      </p>
      <p className="text-xl font-semibold text-zinc-900">{name || "—"}</p>
      <div className="mt-2 flex gap-4 text-sm text-zinc-600">
        <span>Flying from <strong className="text-zinc-900">{origin}</strong></span>
        <span>·</span>
        <span>{travelerLabel}</span>
      </div>
    </div>
  );
}
