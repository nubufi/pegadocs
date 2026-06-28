"use client";

import { create } from "zustand";
import {
  createJSONStorage,
  persist,
  type StateStorage,
} from "zustand/middleware";
import { authApi } from "@/lib/api/auth";
import type {
  AuthResponse,
  AuthUser,
  LoginRequest,
  RegisterRequest,
} from "@/types/auth";

const DEMO_EMAIL = "demo@pegadocs.local";
const DEMO_PASSWORD = "demo1234";
const serverStorage: StateStorage = {
  getItem: () => null,
  setItem: () => undefined,
  removeItem: () => undefined,
};

type AuthState = {
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  expiresAt: number | null;
  hydrated: boolean;
  setHydrated: () => void;
  setSession: (response: AuthResponse) => void;
  clearSession: () => void;
  login: (input: LoginRequest) => Promise<void>;
  register: (input: RegisterRequest) => Promise<string>;
  forgotPassword: (email: string) => Promise<string>;
  resetPassword: (accessToken: string, newPassword: string) => Promise<string>;
  refreshSession: () => Promise<boolean>;
};

function toSession(response: AuthResponse) {
  return {
    user: {
      userId: response.user_id,
      email: response.email,
      name: response.name ?? null,
    },
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    expiresAt: Date.now() + response.expires_in * 1000,
  };
}

function demoSession(email: string): AuthResponse {
  return {
    user_id: "demo-user",
    email,
    name: "Demo User",
    access_token: "demo-access-token",
    refresh_token: "demo-refresh-token",
    expires_in: 60 * 60 * 24,
    token_type: "bearer",
  };
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      expiresAt: null,
      hydrated: false,

      setHydrated: () => set({ hydrated: true }),

      setSession: (response) => set(toSession(response)),

      clearSession: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          expiresAt: null,
        }),

      login: async (input) => {
        if (input.email === DEMO_EMAIL && input.password === DEMO_PASSWORD) {
          set(toSession(demoSession(input.email)));
          return;
        }

        const response = await authApi.login(input);
        set(toSession(response));
      },

      register: async (input) => {
        const response = await authApi.register(input);
        return response.message;
      },

      forgotPassword: async (email) => {
        const response = await authApi.forgotPassword({ email });
        return response.message;
      },

      resetPassword: async (accessToken, newPassword) => {
        const response = await authApi.resetPassword({
          access_token: accessToken,
          new_password: newPassword,
        });
        return response.message;
      },

      refreshSession: async () => {
        const { refreshToken, user } = get();
        if (!refreshToken) return false;

        if (refreshToken === "demo-refresh-token" && user) {
          set(toSession(demoSession(user.email)));
          return true;
        }

        try {
          const response = await authApi.refresh({ refresh_token: refreshToken });
          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            expiresAt: Date.now() + response.expires_in * 1000,
          });
          return true;
        } catch {
          get().clearSession();
          return false;
        }
      },
    }),
    {
      name: "pegadocs-auth",
      storage: createJSONStorage(() =>
        typeof window === "undefined" ? serverStorage : localStorage,
      ),
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        expiresAt: state.expiresAt,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated();
      },
    },
  ),
);

export function getInitials(user: AuthUser | null) {
  const source = user?.name || user?.email || "PegaDocs";
  const parts = source
    .replace(/@.*/, "")
    .split(/[.\s_-]+/)
    .filter(Boolean);

  return parts
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}
