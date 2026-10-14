import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createUser, Gender, UserOut } from "../api/users";
import { Card } from "../components/Card";
import { useUser } from "../state/user";

interface FormState {
  height_cm: string;
  weight_kg: string;
  age: string;
  gender: Gender;
  target_weight_kg: string;
  budget_inr: string;
  city: string;
  vegetarian: boolean;
  gym_available: boolean;
  schedule: string;
}

const blank: FormState = {
  height_cm: "",
  weight_kg: "",
  age: "",
  gender: "male",
  target_weight_kg: "",
  budget_inr: "3000",
  city: "",
  vegetarian: true,
  gym_available: true,
  schedule: "",
};

export default function Onboarding() {
  const nav = useNavigate();
  const { setUser } = useUser();
  const [form, setForm] = useState<FormState>(blank);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const update = <K extends keyof FormState>(k: K, v: FormState[K]) => setForm({ ...form, [k]: v });

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    try {
      const payload = {
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
        age: Number(form.age),
        gender: form.gender,
        target_weight_kg: Number(form.target_weight_kg),
        budget_inr: Number(form.budget_inr),
        city: form.city,
        vegetarian: form.vegetarian,
        gym_available: form.gym_available,
        schedule: form.schedule,
      };
      const user: UserOut = await createUser(payload);
      setUser(user);
      nav("/upload");
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card title="Tell us about yourself">
        <form onSubmit={submit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Height (cm)">
            <input required type="number" value={form.height_cm}
              onChange={(e) => update("height_cm", e.target.value)}
              className="input" />
          </Field>
          <Field label="Weight (kg)">
            <input required type="number" value={form.weight_kg}
              onChange={(e) => update("weight_kg", e.target.value)}
              className="input" />
          </Field>
          <Field label="Age">
            <input required type="number" value={form.age}
              onChange={(e) => update("age", e.target.value)}
              className="input" />
          </Field>
          <Field label="Gender">
            <select value={form.gender} onChange={(e) => update("gender", e.target.value as Gender)} className="input">
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </Field>
          <Field label="Target weight (kg)">
            <input required type="number" value={form.target_weight_kg}
              onChange={(e) => update("target_weight_kg", e.target.value)}
              className="input" />
          </Field>
          <Field label="Budget (₹ / month)">
            <input required type="number" value={form.budget_inr}
              onChange={(e) => update("budget_inr", e.target.value)}
              className="input" />
          </Field>
          <Field label="City">
            <input required type="text" value={form.city}
              onChange={(e) => update("city", e.target.value)}
              className="input" />
          </Field>
          <Field label="Daily schedule">
            <input type="text" value={form.schedule}
              placeholder="e.g. desk job, walk 30 min, gym 3x/week"
              onChange={(e) => update("schedule", e.target.value)}
              className="input" />
          </Field>

          <div className="col-span-1 sm:col-span-2 flex flex-wrap gap-6 pt-1">
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input type="checkbox" checked={form.vegetarian}
                onChange={(e) => update("vegetarian", e.target.checked)} />
              Vegetarian
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input type="checkbox" checked={form.gym_available}
                onChange={(e) => update("gym_available", e.target.checked)} />
              Gym available
            </label>
          </div>

          {err && <div className="col-span-2 text-sm text-red-600">{err}</div>}

          <div className="col-span-1 sm:col-span-2">
            <button disabled={busy} className="w-full bg-brand-600 hover:bg-brand-700 text-white rounded-lg py-2.5 font-medium disabled:opacity-60">
              {busy ? "Saving…" : "Continue → Upload photos"}
            </button>
          </div>
        </form>
      </Card>

      <style>{`
        .input { width: 100%; border: 1px solid #cbd5e1; border-radius: 0.5rem; padding: 0.5rem 0.75rem; font-size: 0.9rem; }
        .input:focus { outline: 2px solid #3b82f6; outline-offset: -1px; }
      `}</style>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1 text-sm text-slate-700">
      <span className="font-medium">{label}</span>
      {children}
    </label>
  );
}
