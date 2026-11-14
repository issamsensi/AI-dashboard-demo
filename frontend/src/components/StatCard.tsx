export function StatCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="glass rounded-3xl p-5 shadow-lg shadow-black/5">
      <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">{label}</div>
      <div className="mt-3 text-3xl font-display font-bold tracking-tight">{value}</div>
      <div className="mt-2 text-sm text-[var(--muted)]">{hint}</div>
    </div>
  );
}
