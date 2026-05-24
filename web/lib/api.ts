import type { Profile, PlanRequest, PlanResponse } from "@/types";

// Set NEXT_PUBLIC_API_URL in .env.local to override.
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getProfile(): Promise<Profile> {
  const res = await fetch(`${BASE}/api/profile`);
  if (!res.ok) throw new Error(`Profile fetch failed: ${res.status}`);
  return res.json() as Promise<Profile>;
}

export async function saveProfile(data: Partial<Profile>): Promise<Profile> {
  const res = await fetch(`${BASE}/api/profile`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Profile save failed: ${res.status}`);
  return res.json() as Promise<Profile>;
}

export async function runPlan(req: PlanRequest): Promise<PlanResponse> {
  const res = await fetch(`${BASE}/api/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(err.detail ?? `Planning failed: ${res.status}`);
  }
  return res.json() as Promise<PlanResponse>;
}
