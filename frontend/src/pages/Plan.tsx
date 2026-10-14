import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getPlan } from "../api/plan";
import { Card } from "../components/Card";
import { useUser } from "../state/user";

type Tab = "roadmap" | "grocery" | "workout";

export default function Plan() {
  const { user } = useUser();
  const [tab, setTab] = useState<Tab>("roadmap");
  const plan = useQuery({
    queryKey: ["plan", user?.id],
    queryFn: () => getPlan(user!.id),
    enabled: !!user,
  });

  if (!user) return <Card><p>Please <a className="text-brand-600" href="/onboarding">complete onboarding</a> first.</p></Card>;
  if (plan.isLoading) return <Card>Loading plan…</Card>;
  if (plan.isError) return <Card><p className="text-red-600">{(plan.error as Error).message}</p></Card>;
  if (!plan.data) return <Card>No plan yet.</Card>;

  const { roadmap, grocery, predicted_target_date } = plan.data;

  return (
    <div className="space-y-4">
      {predicted_target_date && (
        <Card>
          <div className="text-sm text-slate-500">Predicted target date</div>
          <div className="text-2xl font-bold text-brand-700">{predicted_target_date}</div>
        </Card>
      )}

      <div className="flex gap-2 border-b border-slate-200">
        {(["roadmap", "grocery", "workout"] as Tab[]).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium capitalize ${tab === t ? "border-b-2 border-brand-600 text-brand-700" : "text-slate-500 hover:text-slate-700"}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === "roadmap" && (
        <div className="space-y-3">
          {roadmap.map((w) => (
            <Card key={w.week} title={`Week ${w.week}`}>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                <Stat label="Calories" value={`${w.calories} kcal`} />
                <Stat label="Protein" value={`${w.protein_g} g`} />
                <Stat label="Carbs" value={`${w.carbs_g} g`} />
                <Stat label="Fats" value={`${w.fats_g} g`} />
              </div>
              <div className="mt-3 text-sm text-slate-600">
                <span className="font-medium">Focus:</span> {w.workout_focus}
              </div>
              {w.notes && <div className="text-xs text-slate-500 mt-1">{w.notes}</div>}
            </Card>
          ))}
        </div>
      )}

      {tab === "grocery" && (
        <div className="space-y-3">
          {grocery.map((g) => (
            <Card key={g.week} title={`Week ${g.week} grocery list — ₹${g.total_inr.toFixed(0)}`}>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-slate-500 border-b">
                    <th className="py-1">Item</th>
                    <th className="py-1">Qty</th>
                    <th className="py-1 text-right">Price</th>
                  </tr>
                </thead>
                <tbody>
                  {g.items.map((it, i) => (
                    <tr key={i} className="border-b last:border-0">
                      <td className="py-1.5"><span className="text-xs text-slate-400 mr-1">[{it.category}]</span>{it.name}</td>
                      <td className="py-1.5">{it.qty} {it.unit}</td>
                      <td className="py-1.5 text-right">₹{it.est_price.toFixed(0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          ))}
        </div>
      )}

      {tab === "workout" && (
        <div className="space-y-3">
          {roadmap.map((w) => (
            <Card key={w.week} title={`Week ${w.week} workout — ${w.workout_focus}`}>
              <div className="space-y-3">
                {w.workout_days.map((d) => (
                  <div key={d.day}>
                    <div className="text-sm font-medium text-slate-700">Day {d.day} — {d.title}</div>
                    <ul className="text-sm text-slate-600 mt-1 space-y-1">
                      {d.exercises.map((ex) => (
                        <li key={ex.name} className="flex justify-between items-center">
                          <span>
                            <a href={ex.video_url} target="_blank" rel="noreferrer" className="text-brand-600 hover:underline">
                              {ex.name}
                            </a>
                            <span className="text-xs text-slate-400 ml-2">({ex.target_muscle})</span>
                          </span>
                          <span className="text-xs text-slate-500">{ex.sets} × {ex.reps}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-50 rounded-lg p-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="font-semibold text-slate-800">{value}</div>
    </div>
  );
}
