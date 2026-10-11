// frontend/app/context/AuthContext.tsx
"use client";

import React, {createContext, useContext, useEffect, useState, ReactNode} from "react";
import {api} from "../api/client";

type User = {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({children}: {children: ReactNode}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    try {
      const data = await api<User>("/api/auth/me");
      setUser(data);
    } catch (_) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({email, password}),
    });
    await refresh();
  };

  const logout = async () => {
    setLoading(true);
    await api("/api/auth/logout", {method: "POST"});
    setUser(null);
    setLoading(false);
  };

  return (
    <AuthContext.Provider value={{user, loading, login, logout, refresh}}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
