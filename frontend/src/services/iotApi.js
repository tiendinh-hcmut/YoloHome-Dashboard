import apiClient from "./apiClient";

export async function getLatestSensor(deviceId = "") {
  const query = deviceId ? `?device_id=${deviceId}` : "";
  const { data } = await apiClient.get(`/api/sensors/latest${query}`);
  return data;
}

export async function getSensorHistory(deviceId = "", limit = 20) {
  const query = new URLSearchParams();
  if (deviceId) query.append("device_id", deviceId);
  query.append("limit", String(limit));

  const { data } = await apiClient.get(`/api/sensors/history?${query.toString()}`);
  return data;
}

export async function getDeviceStatus(deviceId) {
  const { data } = await apiClient.get(`/api/devices/status?device_id=${deviceId}`);
  return data;
}

export async function controlDevice(deviceId, payload) {
  const { data } = await apiClient.post("/api/devices/control", {
    device_id: deviceId,
    ...payload,
  });
  return data;
}