import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getMe, login as loginApi, logout as logoutApi } from "../services/authApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("current_user");
    return raw ? JSON.parse(raw) : null;
  });
  const [loadingAuth, setLoadingAuth] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoadingAuth(false);
      return;
    }

    getMe()
      .then((data) => setUser(data))
      .catch(() => logout())
      .finally(() => setLoadingAuth(false));
  }, []);

  const login = async (username, password) => {
    const data = await loginApi(username, password);
    setUser(data.user);
    return data;
  };

  const logout = () => {
    logoutApi();
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, loadingAuth, login, logout, isAuthenticated: Boolean(user) }),
    [user, loadingAuth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
