function Pulse({ className }: { className: string }) {
  return <div className={`shimmer rounded ${className}`} />;
}

export function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {/* WinnerHero skeleton */}
      <div className="rounded-3xl bg-white border border-zinc-200 shadow-sm overflow-hidden">
        {/* Dark header skeleton */}
        <div className="bg-zinc-900 px-6 py-6 space-y-3">
          <div className="flex justify-between items-start">
            <Pulse className="h-2.5 w-20 opacity-30" />
            <div className="w-[72px] h-[72px] rounded-full border-2 border-white/10 opacity-20" />
          </div>
          <Pulse className="h-7 w-52 opacity-30" />
          <Pulse className="h-2.5 w-36 opacity-20" />
          <div className="flex gap-3 pt-1">
            <Pulse className="h-3 w-16 opacity-20" />
            <Pulse className="h-3 w-4 opacity-20" />
            <Pulse className="h-3 w-20 opacity-20" />
          </div>
        </div>

        {/* Stats strip skeleton */}
        <div className="grid grid-cols-3 gap-px bg-zinc-100">
          {[0, 1, 2].map((i) => (
            <div key={i} className="bg-white px-4 py-4 flex flex-col items-center gap-2">
              <Pulse className="h-2.5 w-12" />
              <Pulse className="h-5 w-16" />
            </div>
          ))}
        </div>

        {/* Body skeleton */}
        <div className="p-6 space-y-3">
          <Pulse className="h-2.5 w-24" />
          <Pulse className="h-3 w-full" />
          <Pulse className="h-3 w-5/6" />
          <Pulse className="h-3 w-3/4" />
        </div>
      </div>

      {/* Alternative tile skeletons */}
      {[0, 1].map((i) => (
        <div
          key={i}
          className="rounded-2xl bg-white border border-zinc-200 shadow-sm p-4 flex items-center justify-between gap-4"
        >
          <div className="flex items-center gap-3">
            <Pulse className="h-7 w-7 rounded-full" />
            <div className="space-y-2">
              <Pulse className="h-3.5 w-40" />
              <Pulse className="h-2.5 w-28" />
            </div>
          </div>
          <Pulse className="h-12 w-12 rounded-full" />
        </div>
      ))}
    </div>
  );
}
