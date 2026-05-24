function Pulse({ className }: { className: string }) {
  return <div className={`bg-zinc-200 rounded animate-pulse ${className}`} />;
}

export function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {/* WinnerHero skeleton */}
      <div className="rounded-3xl bg-white border border-zinc-200 shadow-sm overflow-hidden">
        <div className="bg-zinc-100 px-6 py-6 space-y-3">
          <div className="flex justify-between items-start">
            <Pulse className="h-2.5 w-20" />
            <Pulse className="h-8 w-14 rounded-lg" />
          </div>
          <Pulse className="h-7 w-52" />
          <Pulse className="h-2.5 w-36" />
          <div className="flex gap-2 pt-1">
            <Pulse className="h-3 w-16" />
            <Pulse className="h-3 w-4" />
            <Pulse className="h-3 w-20" />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-px bg-zinc-100">
          {[0, 1, 2].map((i) => (
            <div key={i} className="bg-white px-4 py-4 flex flex-col items-center gap-2">
              <Pulse className="h-2.5 w-12" />
              <Pulse className="h-5 w-16" />
            </div>
          ))}
        </div>

        <div className="p-6 space-y-3">
          <Pulse className="h-2.5 w-24" />
          <Pulse className="h-3 w-full" />
          <Pulse className="h-3 w-5/6" />
          <Pulse className="h-3 w-3/4" />
        </div>
      </div>

      {/* Alternative tiles skeleton */}
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
          <Pulse className="h-6 w-8" />
        </div>
      ))}
    </div>
  );
}
