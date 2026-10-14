import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getAnalysisHistory, getLatestAnalysis } from "../api/analysis";
import { Card } from "../components/Card";
import { StatTile } from "../components/StatTile";
import { useUser } from "../state/user";

export default function Analysis() {
  const { user } = useUser();
  const latest = useQuery({
    queryKey: ["analysis", "latest", user?.id],
    queryFn: () => getLatestAnalysis(user!.id),
    enabled: !!user,
  });
  const history = useQuery({
    queryKey: ["analysis", "history", user?.id],
    queryFn: () => getAnalysisHistory(user!.id),
    enabled: !!user,
  });

  if (!user) return <Card><p>Please <a className="text-brand-600" href="/onboarding">complete onboarding</a> first.</p></Card>;
  if (latest.isLoading) return <Card>Loading analysis…</Card>;
  if (latest.isError) return <Card><p className="text-red-600">{(latest.error as Error).message}</p></Card>;
  if (!latest.data) return <Card>No analysis yet.</Card>;

  const a = latest.data;
  const chartData = (history.data || []).map((h, i) => ({
    name: `Week ${i + 1}`,
    "Body Fat %": h.body_fat_pct,
    "Muscle (kg)": h.muscle_mass_kg,
    "Posture": h.posture_score,
  }));

  return (
    <div className="space-y-4">
      <Card title="Your body analysis">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatTile label="Body Fat" value={`${a.body_fat_pct}%`} sub="estimated" />
          <StatTile label="Muscle Mass" value={`${a.muscle_mass_kg} kg`} sub={`lean ${a.lean_mass_kg} kg`} />
          <StatTile label="Posture Score" value={`${a.posture_score}/100`} sub="0=poor · 100=ideal" />
          <StatTile label="Fat Pattern" value={a.fat_distribution.pattern || "—"} sub={a.fat_distribution.primary_region || ""} />
        </div>
      </Card>

      <Card title="Weak muscles detected">
        {a.weak_muscles.length ? (
          <div className="flex flex-wrap gap-2">
            {a.weak_muscles.map((m) => (
              <span key={m} className="px-3 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-full text-xs">
                {m.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        ) : <p className="text-slate-500 text-sm">No major imbalances detected.</p>}
      </Card>

      {a.notes && (
        <Card title="AI notes">
          <p className="text-sm text-slate-700">{a.notes}</p>
        </Card>
      )}

      {chartData.length > 1 && (
        <Card title="Progress over time">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="Body Fat %" fill="#3b82f6" />
              <Bar dataKey="Muscle (kg)" fill="#10b981" />
              <Bar dataKey="Posture" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      <div className="text-center">
        <a href="/plan" className="inline-block bg-brand-600 hover:bg-brand-700 text-white rounded-lg py-2.5 px-6 font-medium">
          See your 12-week plan →
        </a>
      </div>
    </div>
  );
}
