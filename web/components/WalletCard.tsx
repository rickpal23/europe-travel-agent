import type { Wallet } from "@/types";

function fmt(n: number) {
  return n >= 1000 ? `${(n / 1000).toFixed(0)}k` : String(n);
}

export function WalletCard({ wallet }: { wallet: Wallet }) {
  return (
    <div className="rounded-2xl bg-white border border-zinc-200 p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3">
        Points Wallet
      </p>
      <div className="flex gap-6 flex-wrap">
        <Stat label="Amex MR" value={fmt(wallet.amex_mr)} />
        <Stat label="Bonvoy pts" value={fmt(wallet.bonvoy_points)} />
        <Stat label="Free nights" value={String(wallet.marriott_free_nights)} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="text-lg font-semibold text-zinc-900">{value}</p>
    </div>
  );
}
