import { ReactNode } from "react";

export function Card({ title, children, className = "" }: { title?: string; children: ReactNode; className?: string }) {
  return (
    <section className={`bg-white rounded-2xl shadow-sm border border-slate-200 p-5 ${className}`}>
      {title && <h2 className="text-lg font-semibold text-slate-800 mb-3">{title}</h2>}
      {children}
    </section>
  );
}
