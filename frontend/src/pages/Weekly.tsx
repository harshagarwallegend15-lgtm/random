import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { reanalyze } from "../api/analysis";
import { generatePlan } from "../api/plan";
import { Card } from "../components/Card";
import { useUser } from "../state/user";

type Angle = "front" | "side" | "back";
const ANGLES: Angle[] = ["front", "side", "back"];

export default function Weekly() {
  const { user } = useUser();
  const qc = useQueryClient();
  const [files, setFiles] = useState<Partial<Record<Angle, File>>>({});
  const [previews, setPreviews] = useState<Partial<Record<Angle, string>>>({});
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const onFile = (angle: Angle, file: File | null) => {
    if (!file) return;
    setFiles((f) => ({ ...f, [angle]: file }));
    const reader = new FileReader();
    reader.onload = () => setPreviews((p) => ({ ...p, [angle]: reader.result as string }));
    reader.readAsDataURL(file);
  };

  if (!user) return <Card><p>Please <a className="text-brand-600" href="/onboarding">complete onboarding</a> first.</p></Card>;

  const submit = async () => {
    if (!files.front || !files.side || !files.back) {
      setErr("Upload all 3 photos.");
      return;
    }
    setErr(null);
    setBusy(true);
    try {
      await reanalyze(user.id, files as { front: File; side: File; back: File });
      await generatePlan(user.id);
      await qc.invalidateQueries({ queryKey: ["analysis"] });
      await qc.invalidateQueries({ queryKey: ["plan"] });
      alert("Re-analyse complete! Adjusted plan is ready.");
      setFiles({});
      setPreviews({});
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <Card title="Weekly re-check-in">
        <p className="text-sm text-slate-600 mb-4">
          Upload 3 fresh photos every week. The AI will compare with last week, adjust calories/workouts, and update your predicted target date.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {ANGLES.map((angle) => (
            <div key={angle} className="border-2 border-dashed border-slate-300 rounded-xl p-3 text-center">
              <div className="text-sm font-semibold capitalize text-slate-700 mb-2">{angle}</div>
              {previews[angle] ? (
                <img src={previews[angle]} alt={angle} className="rounded-lg w-full h-40 object-cover mb-2" />
              ) : (
                <div className="h-40 flex items-center justify-center text-slate-400 text-sm bg-slate-50 rounded-lg mb-2">
                  No image
                </div>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={(e) => onFile(angle, e.target.files?.[0] || null)}
                className="block w-full text-xs"
              />
            </div>
          ))}
        </div>
        {err && <div className="text-sm text-red-600 mt-3">{err}</div>}
        <button onClick={submit} disabled={busy}
          className="mt-5 w-full bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg py-2.5 font-medium disabled:opacity-60">
          {busy ? "Re-analysing…" : "Submit weekly check-in"}
        </button>
      </Card>
    </div>
  );
}
