import { api } from "./client";

export interface AnalysisOut {
  id: number;
  user_id: number;
  photo_set_id: number;
  body_fat_pct: number;
  muscle_mass_kg: number;
  lean_mass_kg: number;
  posture_score: number;
  weak_muscles: string[];
  fat_distribution: Record<string, string>;
  notes: string | null;
  created_at: string;
}

export const uploadPhotos = (userId: number, files: { front: File; side: File; back: File }) => {
  const fd = new FormData();
  fd.append("user_id", String(userId));
  fd.append("front", files.front);
  fd.append("side", files.side);
  fd.append("back", files.back);
  return api
    .post<AnalysisOut>("/photos/upload", fd, { headers: { "Content-Type": "multipart/form-data" } })
    .then((r) => r.data);
};

export const reanalyze = (userId: number, files: { front: File; side: File; back: File }) => {
  const fd = new FormData();
  fd.append("user_id", String(userId));
  fd.append("front", files.front);
  fd.append("side", files.side);
  fd.append("back", files.back);
  return api
    .post<AnalysisOut>(`/reanalyze/${userId}`, fd, { headers: { "Content-Type": "multipart/form-data" } })
    .then((r) => r.data);
};

export const getLatestAnalysis = (userId: number) =>
  api.get<AnalysisOut>(`/analysis/${userId}/latest`).then((r) => r.data);

export const getAnalysisHistory = (userId: number) =>
  api.get<AnalysisOut[]>(`/analysis/${userId}/history`).then((r) => r.data);
