"use client";

import { useState, useEffect } from "react";
import { LoadingSkeleton } from "./LoadingSkeleton";

const TAGLINES = [
  "Converting your points into memories…",
  "Consulting the Bonvoy oracle…",
  "Hunting for lie-flat seats…",
  "Stretching your points farther than coach…",
  "Finding the sweet spot between luxury and sanity…",
  "Arguing with algorithms so you don't have to…",
  "Scanning the award calendar for hidden gems…",
];

function buildSteps(origin: string, cities: string[]): string[] {
  const first = cities[0] ?? "your destination";
  const cityList = cities.slice(0, 2).join(" + ") || first;
  return [
    `Searching award space for ${origin} → ${first}…`,
    `Checking hotel availability in ${cityList}…`,
    `Evaluating transfer partner options…`,
    `Ranking itinerary combinations…`,
    `Optimizing family comfort score…`,
    `Calculating points redemption value…`,
    `Finalizing your best match…`,
  ];
}

export function PlanningOverlay({
  origin,
  cities,
}: {
  origin: string;
  cities: string[];
}) {
  const steps = buildSteps(origin, cities);

  const [stepIdx, setStepIdx] = useState(0);
  const [stepVisible, setStepVisible] = useState(true);
  const [taglineIdx, setTaglineIdx] = useState(0);
  const [taglineVisible, setTaglineVisible] = useState(true);
  const [progress, setProgress] = useState(0);

  // Cycle planning steps with crossfade
  useEffect(() => {
    const t = setInterval(() => {
      setStepVisible(false);
      setTimeout(() => {
        setStepIdx((i) => (i + 1) % steps.length);
        setStepVisible(true);
      }, 220);
    }, 2800);
    return () => clearInterval(t);
  }, [steps.length]);

  // Cycle taglines with crossfade
  useEffect(() => {
    const t = setInterval(() => {
      setTaglineVisible(false);
      setTimeout(() => {
        setTaglineIdx((i) => (i + 1) % TAGLINES.length);
        setTaglineVisible(true);
      }, 280);
    }, 4500);
    return () => clearInterval(t);
  }, []);

  // Fake asymptotic progress: fast start, slows toward ~85%
  useEffect(() => {
    const t = setInterval(() => {
      setProgress((p) => {
        const next = p + (84 - p) * 0.05;
        return next;
      });
    }, 500);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="space-y-4">
      {/* Progress card */}
      <div className="rounded-2xl bg-white border border-zinc-200 shadow-sm px-6 py-5 space-y-4 fade-up">
        {/* Tagline */}
        <p
          className="text-xs font-medium text-zinc-400 tracking-wide"
          style={{
            opacity: taglineVisible ? 1 : 0,
            transition: "opacity 0.28s ease",
          }}
        >
          {TAGLINES[taglineIdx]}
        </p>

        {/* Current step */}
        <p
          className="text-sm font-semibold text-zinc-800"
          style={{
            opacity: stepVisible ? 1 : 0,
            transition: "opacity 0.22s ease",
          }}
        >
          {steps[stepIdx]}
        </p>

        {/* Progress bar */}
        <div className="space-y-2">
          <div className="h-1 bg-zinc-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-zinc-800 rounded-full"
              style={{
                width: `${progress}%`,
                transition: "width 0.6s cubic-bezier(0.4, 0, 0.2, 1)",
              }}
            />
          </div>

          {/* Step dots */}
          <div className="flex gap-1">
            {steps.map((_, i) => (
              <div
                key={i}
                className="h-0.5 flex-1 rounded-full transition-colors duration-700"
                style={{
                  backgroundColor: i <= stepIdx ? "#27272a" : "#e4e4e7",
                }}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Skeleton result cards */}
      <LoadingSkeleton />
    </div>
  );
}
