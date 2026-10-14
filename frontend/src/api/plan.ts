import { api } from "./client";

export interface Exercise { name: string; sets: number; reps: string; video_url: string; target_muscle: string; }
export interface WorkoutDay { day: number; title: string; exercises: Exercise[]; }
export interface RoadmapWeek {
  week: number;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  workout_focus: string;
  notes: string | null;
  workout_days: WorkoutDay[];
}
export interface GroceryItem { name: string; qty: number; unit: string; est_price: number; category: string; }
export interface GroceryList { week: number; total_inr: number; items: GroceryItem[]; }
export interface PlanOut {
  user_id: number;
  weeks: number;
  roadmap: RoadmapWeek[];
  grocery: GroceryList[];
  predicted_target_weeks: number;
  predicted_target_date: string | null;
}

export const generatePlan = (userId: number) =>
  api.post<PlanOut>(`/plan/${userId}/generate`).then((r) => r.data);

export const getPlan = (userId: number) =>
  api.get<PlanOut>(`/plan/${userId}`).then((r) => r.data);
