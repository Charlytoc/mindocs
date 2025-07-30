import { create } from "zustand";

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const { login } = await import("../utils/api");
      const response = await login(email, password);

      // For now, we'll create a user object from the email
      // In a real app, the backend would return user details
      const user: User = {
        id: response.user_id || email,
        email,
        name: email.split("@")[0], // Simple name extraction
      };

      set({ user, isAuthenticated: true, isLoading: false });

      // Store in localStorage for persistence
      localStorage.setItem("user", JSON.stringify(user));
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  signup: async (email: string, password: string, name?: string) => {
    set({ isLoading: true });
    try {
      const { signup } = await import("../utils/api");
      await signup(email, password, name);

      // After signup, automatically log in
      await get().login(email, password);
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    set({ user: null, isAuthenticated: false });
    localStorage.removeItem("user");
  },

  setUser: (user: User) => {
    set({ user, isAuthenticated: true });
  },
}));

// Initialize auth state from localStorage
if (typeof window !== "undefined") {
  const storedUser = localStorage.getItem("user");
  if (storedUser) {
    try {
      const user = JSON.parse(storedUser);
      useAuthStore.getState().setUser(user);
    } catch (error) {
      console.error("Error parsing stored user:", error);
      localStorage.removeItem("user");
    }
  }
}
