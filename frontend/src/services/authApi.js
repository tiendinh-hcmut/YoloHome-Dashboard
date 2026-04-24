import apiClient from "./apiClient";

export async function login(username, password) {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  const { data } = await apiClient.post("/api/auth/token", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("current_user", JSON.stringify(data.user));
  return data;
}

export async function getMe() {
  const { data } = await apiClient.get("/api/auth/me");
  localStorage.setItem("current_user", JSON.stringify(data));
  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("current_user");
}
