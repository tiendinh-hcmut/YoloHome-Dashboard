import { useEffect, useState } from "react";
import {
  getLatestSensor,
  getSensorHistory,
  getDeviceStatus,
  controlDevice,
} from "../../services/iotApi";
import Topbar from "../../components/layout/Topbar";
import SensorHistoryCard from "../../components/dashboard/iot/SensorHistoryCard";
import IotVisualBoard from "../../components/dashboard/iot/IotVisualBoard";

export default function IotDashboard() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [deviceId, setDeviceId] = useState("esp32");
  const [deviceState, setDeviceState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [controlling, setControlling] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [error, setError] = useState("");

  const fetchIotData = async () => {
    setLoading(true);
    setError("");

    try {
      const latestRes = await getLatestSensor(deviceId);
      const historyRes = await getSensorHistory(deviceId, 20);
      const deviceRes = await getDeviceStatus(deviceId);

      setLatest(latestRes);
      setHistory(historyRes.items || []);
      setDeviceState(deviceRes);
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Không tải được dữ liệu IoT từ database."
      );
      setLatest(null);
      setHistory([]);
      setDeviceState(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIotData();

    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchIotData();
    }, 5000);

    return () => clearInterval(interval);
  }, [deviceId, autoRefresh]);

  const handleToggleLed = async () => {
    if (!deviceId) return;

    const previousState = deviceState?.led ?? false;
    const nextValue = !previousState;

    setDeviceState((prev) => ({
      ...(prev || { device_id: deviceId }),
      led: nextValue,
    }));

    try {
      setControlling(true);
      const res = await controlDevice(deviceId, { led: nextValue });
      setDeviceState((prev) => ({
        ...(prev || {}),
        ...res,
      }));
    } catch (err) {
      console.error(err);
      setDeviceState((prev) => ({
        ...(prev || { device_id: deviceId }),
        led: previousState,
      }));
      alert("Không điều khiển được LED.");
    } finally {
      setControlling(false);
    }
  };

  return (
    <>
      <Topbar
        title="IoT Dashboard"
        subtitle="Hiển thị dữ liệu từ Adafruit đã đồng bộ về MongoDB."
      />

      {error ? <div className="global-error">{error}</div> : null}

      <section className="card">
        <div className="card-header">
          <h2>
            <span className="title-icon">🔎</span>Bộ lọc thiết bị
          </h2>
          <span className="tag blue">Filter</span>
        </div>

        <div className="upload-box">
          <input
            type="text"
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
            placeholder="Nhập device_id"
          />

          <button className="primary-btn" onClick={fetchIotData} disabled={loading}>
            {loading ? "Đang tải..." : "Tải dữ liệu IoT"}
          </button>

          <button
            className="warning-btn"
            onClick={() => setAutoRefresh((v) => !v)}
          >
            {autoRefresh ? "Tắt auto refresh 5s" : "Bật auto refresh 5s"}
          </button>

          <div className="soft-note">
            Auto refresh: <strong>{autoRefresh ? "ON" : "OFF"}</strong>
          </div>
        </div>
      </section>

      <div className="dashboard-column">
        <IotVisualBoard
          latest={latest}
          deviceState={deviceState}
          onToggleLed={handleToggleLed}
          controlling={controlling}
        />
        <SensorHistoryCard history={history} />
      </div>
    </>
  );
}