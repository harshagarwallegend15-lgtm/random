import { Routes, Route, Navigate } from "react-router-dom";
import Onboarding from "./pages/Onboarding";
import PhotoUpload from "./pages/PhotoUpload";
import Analysis from "./pages/Analysis";
import Plan from "./pages/Plan";
import Weekly from "./pages/Weekly";
import { UserProvider } from "./state/user";

export default function App() {
  return (
    <UserProvider>
      <div className="min-h-screen flex flex-col">
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-800">💪 Workout App</h1>
          <nav className="flex gap-4 text-sm text-slate-600">
            <a className="hover:text-brand-600" href="/onboarding">Profile</a>
            <a className="hover:text-brand-600" href="/upload">Photos</a>
            <a className="hover:text-brand-600" href="/plan">Plan</a>
            <a className="hover:text-brand-600" href="/weekly">Weekly</a>
          </nav>
        </header>
        <main className="flex-1 max-w-5xl w-full mx-auto p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/onboarding" replace />} />
            <Route path="/onboarding" element={<Onboarding />} />
            <Route path="/upload" element={<PhotoUpload />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/plan" element={<Plan />} />
            <Route path="/weekly" element={<Weekly />} />
          </Routes>
        </main>
      </div>
    </UserProvider>
  );
}
