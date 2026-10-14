interface Stat { label: string; value: string | number; sub?: string; }

export function StatTile({ label, value, sub }: Stat) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col">
      <span className="text-xs uppercase tracking-wide text-slate-500">{label}</span>
      <span className="text-2xl font-bold text-slate-800 mt-1">{value}</span>
      {sub && <span className="text-xs text-slate-500 mt-1">{sub}</span>}
    </div>
  );
}
