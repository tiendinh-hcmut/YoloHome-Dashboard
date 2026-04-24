import apiClient, { API_BASE_URL } from "./apiClient";

export function toAssetUrl(path) {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return `${API_BASE_URL}${path}`;
}

export async function getHealth() {
  const { data } = await apiClient.get("/api/health");
  return data;
}

export async function detectImage(file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post("/api/detect-image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function detectVideo(file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post("/api/detect-video", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function detectFrame(blob) {
  const formData = new FormData();
  formData.append("file", blob, "frame.jpg");
  const { data } = await apiClient.post("/api/detect-frame", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
