"use client";

import { useState } from "react";
import type {
  Itinerary,
  AwardAvailability,
  FlightPlan,
  HotelPlan,
  DayPlanEntry,
} from "@/types";

// ─── Utilities ────────────────────────────────────────────────────────────────

function fmtPts(n: number | null | undefined): string {
  if (n == null) return "—";
  return n >= 1000 ? `${Math.round(n / 1000)}k` : String(n);
}

function fmtDate(iso: string): string {
  // Append noon to avoid timezone-shifting to previous day
  const d = new Date(iso + "T12:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function fmtDateList(dates: string[], max = 4): string {
  if (!dates?.length) return "";
  const shown = dates.slice(0, max).map(fmtDate).join(", ");
  const extra = dates.length - max;
  return extra > 0 ? `${shown} +${extra} more` : shown;
}

function parseHotelLine(line: string) {
  const EM = " — ";
  const parts = line.split(EM);
  const head = parts[0] ?? "";
  const hotelRoom = parts[1] ?? "";
  const payment = parts.slice(2).join(EM);
  const parenIdx = hotelRoom.indexOf(" (");
  const hotelName = parenIdx > 0 ? hotelRoom.slice(0, parenIdx) : hotelRoom;
  const roomDesc = parenIdx > 0 ? hotelRoom.slice(parenIdx + 2, -1) : "";
  return { head, hotelName, roomDesc, payment };
}

// ─── Accordion ────────────────────────────────────────────────────────────────

function Accordion({
  title,
  summary,
  children,
  dim = false,
}: {
  title: string;
  summary?: string;
  children: React.ReactNode;
  dim?: boolean;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-t border-zinc-100">
      <button
        onClick={() => setOpen(!open)}
        className={`w-full flex items-start justify-between py-4 text-left ${
          dim && !open ? "opacity-50 hover:opacity-80 transition-opacity" : ""
        }`}
      >
        <div className="flex-1 min-w-0 pr-4">
          <span
            className={`text-sm font-semibold ${
              dim ? "text-zinc-500" : "text-zinc-800"
            }`}
          >
            {title}
          </span>
          {!open && summary && (
            <p className="text-xs text-zinc-400 mt-0.5 leading-snug">{summary}</p>
          )}
        </div>
        <span className="shrink-0 text-[10px] text-zinc-400 mt-0.5">
          {open ? "▲" : "▼"}
        </span>
      </button>
      {open && <div className="pb-6 space-y-5">{children}</div>}
    </div>
  );
}

// ─── Small building blocks ────────────────────────────────────────────────────

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-2.5">
      {children}
    </p>
  );
}

function Row({
  label,
  value,
  bold,
  indent,
}: {
  label: string;
  value: string;
  bold?: boolean;
  indent?: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-4 text-sm">
      <span className={`${indent ? "pl-4 text-xs text-zinc-400" : "text-zinc-600"}`}>
        {indent ? `· ${label}` : label}
      </span>
      <span
        className={`shrink-0 ${
          bold
            ? "font-semibold text-zinc-900"
            : indent
            ? "text-xs text-zinc-400"
            : "text-zinc-700"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

function LiveBadge({ source }: { source: string }) {
  const isLive = source === "seats.aero";
  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${
        isLive ? "bg-emerald-50 text-emerald-600" : "bg-zinc-100 text-zinc-500"
      }`}
    >
      <span
        className={`w-1 h-1 rounded-full ${
          isLive ? "bg-emerald-500" : "bg-zinc-400"
        }`}
      />
      {isLive ? "Live · Seats.aero" : "Estimated"}
    </span>
  );
}

// ─── Flights section ─────────────────────────────────────────────────────────

function FlightLeg({
  label,
  avail,
}: {
  label: string;
  avail: AwardAvailability;
}) {
  const ok = avail.available;
  const others = avail.all_programs?.filter((p) => p !== avail.program) ?? [];

  return (
    <div className="space-y-2">
      <SectionLabel>{label}</SectionLabel>

      <div className="flex items-start gap-3">
        <span
          className={`shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] mt-0.5 ${
            ok
              ? "bg-emerald-100 text-emerald-700"
              : "bg-zinc-100 text-zinc-400"
          }`}
        >
          {ok ? "✓" : "—"}
        </span>
        <div className="flex-1 min-w-0 space-y-1">
          <p className="text-sm font-medium text-zinc-900">{avail.route}</p>
          <p className="text-xs text-zinc-500">
            {avail.program}
            {avail.cabin ? ` · ${avail.cabin}` : ""}
            {ok && avail.lowest_points != null
              ? ` · from ${fmtPts(avail.lowest_points)} pts/pax`
              : ""}
          </p>
          {ok && (
            <p className="text-xs text-zinc-400">
              {avail.seat_count} date{avail.seat_count !== 1 ? "s" : ""} with
              space
              {avail.dates_with_space?.length
                ? ` — ${fmtDateList(avail.dates_with_space)}`
                : ""}
            </p>
          )}
          {ok && others.length > 0 && (
            <p className="text-xs text-zinc-400 pt-0.5">
              Also via:{" "}
              {others.slice(0, 5).join(", ")}
              {others.length > 5 ? " +more" : ""}
            </p>
          )}
        </div>
        <LiveBadge source={avail.source} />
      </div>
    </div>
  );
}

function FlightsSection({
  out,
  ret,
  plan,
  transit,
}: {
  out: AwardAvailability;
  ret: AwardAvailability;
  plan?: FlightPlan;
  transit: string[];
}) {
  return (
    <div className="space-y-5">
      <FlightLeg label="Outbound" avail={out} />
      <FlightLeg label="Return" avail={ret} />

      {plan && (
        <div className="rounded-xl bg-zinc-50 p-4 space-y-2.5">
          <SectionLabel>Plan uses</SectionLabel>
          <p className="text-sm text-zinc-700">{plan.outbound}</p>
          <p className="text-sm text-zinc-700">{plan.return}</p>
          {plan.intra_cash > 0 && (
            <p className="text-sm text-zinc-500">
              Intra-Europe transit (trains/buses): ~$
              {plan.intra_cash.toLocaleString()}
            </p>
          )}
        </div>
      )}

      {transit.length > 0 && (
        <div>
          <SectionLabel>Getting around</SectionLabel>
          <ul className="space-y-1.5">
            {transit.map((t, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-zinc-600">
                <span className="text-zinc-300 shrink-0 mt-0.5">→</span>
                {t}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ─── Hotels section ───────────────────────────────────────────────────────────

function HotelsSection({ plan }: { plan: HotelPlan }) {
  return (
    <div className="space-y-5">
      {plan.lines.map((line, i) => {
        const { head, hotelName, roomDesc, payment } = parseHotelLine(line);
        return (
          <div key={i} className="space-y-1.5">
            <p className="text-xs font-semibold text-zinc-400">{head}</p>
            <p className="text-sm font-semibold text-zinc-900">{hotelName}</p>
            {roomDesc && (
              <p className="text-xs text-zinc-500 leading-relaxed">{roomDesc}</p>
            )}
            <span className="inline-flex text-xs px-2.5 py-1 rounded-full bg-zinc-100 text-zinc-600">
              {payment}
            </span>
          </div>
        );
      })}

      <div className="rounded-xl bg-zinc-50 p-4">
        <SectionLabel>Summary</SectionLabel>
        <div className="grid grid-cols-2 gap-x-6 gap-y-3">
          <Stat label="Certs used" value={String(plan.certs_used)} />
          <Stat label="Bonvoy pts" value={fmtPts(plan.points_used)} />
          <Stat
            label="Cash (hotels)"
            value={`$${plan.cash_for_hotels.toLocaleString()}`}
          />
          <Stat
            label="Avg room size"
            value={`${Math.round(plan.avg_sqft)} sqft`}
          />
        </div>
        {plan.small_room_count > 0 && (
          <p className="text-xs text-amber-600 mt-3 pt-3 border-t border-amber-100">
            {plan.small_room_count} room
            {plan.small_room_count > 1 ? "s are" : " is"} under 400 sqft —
            snug for a family of 4. Request connecting room or upgrade at
            check-in.
          </p>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-zinc-400">{label}</p>
      <p className="text-sm font-semibold text-zinc-900">{value}</p>
    </div>
  );
}

// ─── Day-by-day section ───────────────────────────────────────────────────────

function DayPlanSection({ days }: { days: DayPlanEntry[] }) {
  return (
    <div className="space-y-0">
      {days.map((d, i) => (
        <div
          key={d.day}
          className={`flex gap-4 pb-5 ${
            i < days.length - 1
              ? "border-b border-zinc-100 mb-5"
              : ""
          }`}
        >
          {/* Day label */}
          <div className="shrink-0 w-16 text-right pt-0.5">
            <p className="text-xs font-semibold text-zinc-800">Day {d.day}</p>
            <p className="text-[10px] text-zinc-400 mt-0.5 leading-tight">
              {d.date_str}
            </p>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0 space-y-1.5">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-400">
              {d.city}
            </p>
            <p className="text-sm font-medium text-zinc-900 leading-snug">
              {d.main}
            </p>
            {d.lighter && (
              <p className="text-xs text-zinc-500">{d.lighter}</p>
            )}
            {d.family && (
              <p className="text-xs text-zinc-400 italic">{d.family}</p>
            )}
            {d.points_note && (
              <p className="text-xs text-zinc-600 bg-zinc-50 border border-zinc-100 px-3 py-2 rounded-lg mt-2">
                {d.points_note}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Points strategy section ──────────────────────────────────────────────────

function PointsSection({
  plan,
  hotelPlan,
  totalCash,
}: {
  plan: FlightPlan;
  hotelPlan: HotelPlan;
  totalCash: number;
}) {
  return (
    <div className="space-y-5">
      {/* Amex MR */}
      <div>
        <SectionLabel>Amex Membership Rewards</SectionLabel>
        <div className="space-y-1.5">
          <Row
            label={`Flights — ${fmtPts(plan.amex_used)} pts total`}
            value=""
            bold
          />
          <Row
            label={plan.outbound}
            value=""
            indent
          />
          <Row
            label={plan.return}
            value=""
            indent
          />
          {plan.amex_short > 0 && (
            <p className="text-xs text-amber-600 pt-1">
              Short by {fmtPts(plan.amex_short)} pts — consider a Flying Blue
              Saver transfer or partial cash payment.
            </p>
          )}
        </div>
      </div>

      {/* Bonvoy */}
      <div>
        <SectionLabel>Marriott Bonvoy</SectionLabel>
        <div className="space-y-1.5">
          <Row
            label="Free-night certs"
            value={`${hotelPlan.certs_used} certs`}
          />
          <Row
            label="Points (hotel nights)"
            value={`${fmtPts(hotelPlan.points_used)} pts`}
          />
        </div>
      </div>

      {/* Cash */}
      <div>
        <SectionLabel>Cash out-of-pocket</SectionLabel>
        <div className="space-y-1.5">
          <Row
            label="Total"
            value={`~$${totalCash.toLocaleString()}`}
            bold
          />
          {plan.intra_cash > 0 && (
            <Row
              label="Intra-Europe trains / transit"
              value={`~$${plan.intra_cash.toLocaleString()}`}
              indent
            />
          )}
          {hotelPlan.cash_for_hotels > 0 && (
            <Row
              label="Hotel cash nights"
              value={`~$${hotelPlan.cash_for_hotels.toLocaleString()}`}
              indent
            />
          )}
          {plan.flight_cash_overflow > 0 && (
            <Row
              label="Flight cash overflow"
              value={`~$${plan.flight_cash_overflow.toLocaleString()}`}
              indent
            />
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Advanced section ─────────────────────────────────────────────────────────

function AdvancedSection({
  breakdown,
  researchNotes,
}: {
  breakdown: string[];
  researchNotes?: Itinerary["research_notes"];
}) {
  return (
    <div className="space-y-5">
      {breakdown.length > 0 && (
        <div>
          <SectionLabel>Score breakdown</SectionLabel>
          <ul className="space-y-1.5">
            {breakdown.map((b, i) => (
              <li key={i} className="text-xs text-zinc-500">
                {b}
              </li>
            ))}
          </ul>
        </div>
      )}
      {researchNotes && (
        <div className="space-y-3">
          {researchNotes.confidence && (
            <div>
              <SectionLabel>Confidence</SectionLabel>
              <p className="text-xs text-zinc-500">
                {researchNotes.confidence}
              </p>
            </div>
          )}
          {researchNotes.hotel && (
            <div>
              <SectionLabel>Hotel research note</SectionLabel>
              <p className="text-xs text-zinc-500 leading-relaxed">
                {researchNotes.hotel}
              </p>
            </div>
          )}
          {researchNotes.flight && (
            <div>
              <SectionLabel>Flight research note</SectionLabel>
              <p className="text-xs text-zinc-500 leading-relaxed">
                {researchNotes.flight}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Award chips (always-visible summary) ─────────────────────────────────────

function AwardChip({
  label,
  avail,
}: {
  label: string;
  avail: AwardAvailability | null | undefined;
}) {
  if (!avail) return null;
  const ok = avail.available;
  return (
    <div
      className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full ${
        ok ? "bg-emerald-50 text-emerald-700" : "bg-zinc-100 text-zinc-500"
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full shrink-0 ${
          ok ? "bg-emerald-500" : "bg-zinc-400"
        }`}
      />
      {label}:{" "}
      {ok ? (
        <>
          {avail.seat_count} date{avail.seat_count !== 1 ? "s" : ""}
          {avail.lowest_points != null && (
            <span className="opacity-60">
              {" "}
              · {fmtPts(avail.lowest_points)} pts/pax
            </span>
          )}
        </>
      ) : (
        "none found"
      )}
    </div>
  );
}

// ─── Stats strip cell ─────────────────────────────────────────────────────────

function StatCell({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white px-3 py-4 text-center">
      <p className="text-xs text-zinc-400 mb-1.5">{label}</p>
      {children}
    </div>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

const ODDS_STYLE: Record<string, { text: string; dot: string }> = {
  High: { text: "text-emerald-600", dot: "bg-emerald-500" },
  Medium: { text: "text-amber-600", dot: "bg-amber-500" },
  Low: { text: "text-red-600", dot: "bg-red-500" },
};

export function WinnerHero({ itinerary }: { itinerary: Itinerary }) {
  const {
    name,
    stops,
    score,
    total_cash,
    nights,
    award_likelihood,
    dates,
    pros,
    transit = [],
    award_availability: out,
    award_availability_return: ret,
    flight_plan,
    hotel_plan,
    day_plan,
    research_notes,
    breakdown = [],
  } = itinerary;

  const odds = ODDS_STYLE[award_likelihood] ?? ODDS_STYLE.Medium;

  // Total points estimate for stats strip
  const outPts = out?.lowest_points ?? null;
  const retPts = ret?.lowest_points ?? null;
  const totalPts =
    outPts != null && retPts != null
      ? outPts + retPts
      : outPts ?? retPts;

  // Accordion summaries (shown when collapsed)
  const flightSummary = out?.available
    ? `${out.route} · ${out.seat_count} dates · from ${fmtPts(out.lowest_points)} pts via ${out.program}`
    : flight_plan?.outbound ?? "";

  const hotelSummary = hotel_plan
    ? `${hotel_plan.certs_used} cert${hotel_plan.certs_used !== 1 ? "s" : ""} · ${fmtPts(hotel_plan.points_used)} Bonvoy${hotel_plan.cash_for_hotels > 0 ? ` · $${hotel_plan.cash_for_hotels} cash` : ""}`
    : "";

  const dayPlanSummary = day_plan?.length
    ? `${day_plan.length} days · ${stops.map(([c]) => c).join(", ")}`
    : "";

  const pointsSummary = flight_plan
    ? `${fmtPts(flight_plan.amex_used)} MR → flights${hotel_plan ? ` · ${fmtPts(hotel_plan.points_used)} Bonvoy + ${hotel_plan.certs_used} certs → hotels` : ""}`
    : "";

  return (
    <div className="rounded-3xl bg-white border border-zinc-200 shadow-sm overflow-hidden">
      {/* Dark header */}
      <div className="bg-zinc-900 px-6 pt-5 pb-7">
        <div className="flex items-start justify-between mb-4">
          <span className="text-xs font-semibold tracking-widest text-zinc-500 uppercase">
            Best Match
          </span>
          <div className="text-right leading-none">
            <span className="text-4xl font-bold text-white">
              {Math.round(score)}
            </span>
            <span className="text-zinc-500 text-sm"> /100</span>
          </div>
        </div>
        <h2 className="text-2xl font-bold text-white leading-tight">{name}</h2>
        <p className="text-zinc-400 text-sm mt-1">
          {nights} nights · {dates.label}
        </p>
        <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1 mt-4">
          {stops.map(([city, n], i) => (
            <span key={city} className="flex items-center gap-1.5">
              <span className="text-sm font-medium text-white">{city}</span>
              <span className="text-zinc-500 text-xs">{n}n</span>
              {i < stops.length - 1 && (
                <span className="text-zinc-600 text-xs">→</span>
              )}
            </span>
          ))}
        </div>
      </div>

      {/* Stats strip */}
      <div className="grid grid-cols-3 gap-px bg-zinc-100">
        <StatCell label="Est. cash">
          <p className="text-base font-semibold text-zinc-900">
            ${total_cash.toLocaleString()}
          </p>
        </StatCell>
        <StatCell label="Points (est.)">
          <p className="text-base font-semibold text-zinc-900">
            {fmtPts(totalPts)}
          </p>
          {totalPts != null && (
            <p className="text-[10px] text-zinc-400 mt-0.5">lowest/pax</p>
          )}
        </StatCell>
        <StatCell label="Award odds">
          <span
            className={`inline-flex items-center gap-1.5 text-sm font-semibold ${odds.text}`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${odds.dot}`} />
            {award_likelihood}
          </span>
        </StatCell>
      </div>

      {/* Body */}
      <div className="px-6 pt-5 pb-1">
        {/* Live award chips */}
        {(out || ret) && (
          <div className="flex flex-wrap gap-2 mb-5">
            <AwardChip label="Outbound" avail={out} />
            <AwardChip label="Return" avail={ret} />
          </div>
        )}

        {/* Pros — why it works */}
        {pros.length > 0 && (
          <div className="mb-1">
            <SectionLabel>Why it works</SectionLabel>
            <ul className="space-y-2">
              {pros.map((p, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2.5 text-sm text-zinc-700"
                >
                  <span className="text-emerald-500 shrink-0 mt-0.5">✓</span>
                  {p}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Accordion sections */}
      <div className="px-6 pb-4">
        <Accordion title="Flights" summary={flightSummary}>
          <FlightsSection out={out} ret={ret} plan={flight_plan} transit={transit} />
        </Accordion>

        {hotel_plan && (
          <Accordion title="Hotels" summary={hotelSummary}>
            <HotelsSection plan={hotel_plan} />
          </Accordion>
        )}

        {day_plan && day_plan.length > 0 && (
          <Accordion title="Day-by-day plan" summary={dayPlanSummary}>
            <DayPlanSection days={day_plan} />
          </Accordion>
        )}

        {flight_plan && hotel_plan && (
          <Accordion title="Points strategy" summary={pointsSummary}>
            <PointsSection
              plan={flight_plan}
              hotelPlan={hotel_plan}
              totalCash={total_cash}
            />
          </Accordion>
        )}

        {(breakdown.length > 0 || research_notes) && (
          <Accordion title="Advanced details" dim>
            <AdvancedSection
              breakdown={breakdown}
              researchNotes={research_notes}
            />
          </Accordion>
        )}
      </div>
    </div>
  );
}
