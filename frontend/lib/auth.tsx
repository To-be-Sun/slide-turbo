"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import type { User } from "./types";
import { getMe } from "./api";

// ── Dev Mode ─────────────────────────────────
const DEV_MODE = process.env.NODE_ENV === "development";

const DEV_USER: User = {
  id: "dev-user-001",
  email: "dev@slide-turbo.local",
  name: "Dev User",
  icon: null,
  created_at: new Date().toISOString(),
};

const DEV_TOKEN = "dev-token-slide-turbo";

// ── Context ──────────────────────────────────

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  token: string | null;
  isDevMode: boolean;
  login: (token: string, user: User) => void;
  devLogin: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  token: null,
  isDevMode: false,
  login: () => {},
  devLogin: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // 起動時に localStorage からトークンを復元
  useEffect(() => {
    const stored = localStorage.getItem("token");
    if (!stored) {
      setLoading(false);
      return;
    }

    // Dev token の場合は API を叩かずにそのまま復元
    if (stored === DEV_TOKEN) {
      setToken(DEV_TOKEN);
      const storedUser = localStorage.getItem("dev_user");
      setUser(storedUser ? JSON.parse(storedUser) : DEV_USER);
      setLoading(false);
      return;
    }

    setToken(stored);
    getMe()
      .then((u) => setUser(u))
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(
    (newToken: string, newUser: User) => {
      localStorage.setItem("token", newToken);
      setToken(newToken);
      setUser(newUser);
    },
    []
  );

  const devLogin = useCallback(() => {
    localStorage.setItem("token", DEV_TOKEN);
    localStorage.setItem("dev_user", JSON.stringify(DEV_USER));
    setToken(DEV_TOKEN);
    setUser(DEV_USER);
    router.push("/");
  }, [router]);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("dev_user");
    setToken(null);
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{ user, loading, token, isDevMode: DEV_MODE, login, devLogin, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
