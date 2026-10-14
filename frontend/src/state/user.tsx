import { createContext, ReactNode, useContext, useState } from "react";
import type { UserOut } from "../api/users";

interface UserCtx {
  user: UserOut | null;
  setUser: (u: UserOut | null) => void;
}

const Ctx = createContext<UserCtx | null>(null);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(() => {
    const raw = localStorage.getItem("workout_user");
    return raw ? (JSON.parse(raw) as UserOut) : null;
  });

  const update = (u: UserOut | null) => {
    setUser(u);
    if (u) localStorage.setItem("workout_user", JSON.stringify(u));
    else localStorage.removeItem("workout_user");
  };

  return <Ctx.Provider value={{ user, setUser: update }}>{children}</Ctx.Provider>;
}

export function useUser() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useUser must be used inside <UserProvider>");
  return ctx;
}
