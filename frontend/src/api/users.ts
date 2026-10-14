import { api } from "./client";

export type Gender = "male" | "female" | "other";

export interface UserCreate {
  height_cm: number;
  weight_kg: number;
  age: number;
  gender: Gender;
  target_weight_kg: number;
  budget_inr: number;
  city: string;
  vegetarian: boolean;
  gym_available: boolean;
  schedule: string;
}

export interface UserOut extends UserCreate {
  id: number;
  created_at: string;
}

export const createUser = (data: UserCreate) =>
  api.post<UserOut>("/users", data).then((r) => r.data);

export const getUser = (id: number) =>
  api.get<UserOut>(`/users/${id}`).then((r) => r.data);
