function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function toPercent(value, min, max) {
  if (value == null) return 0;
  return Math.round(((value - min) / (max - min)) * 100);
}

function getScore(latest) {
  if (!latest) return 0;

  let score = 100;

  const temp = latest.temperature ?? 0;
  const humidity = latest.humidity ?? 0;
  const lightRaw = latest.light ?? 0;

  if (temp < 21 || temp > 32) score -= 20;
  if (humidity < 40 || humidity > 80) score -= 20;

  const brightnessPercent = clamp(toPercent(lightRaw, 0, 1023), 0, 100);
  if (brightnessPercent < 60 || brightnessPercent > 100) score -= 20;

  return clamp(score, 0, 100);
}

function getStatus(score) {
  if (score >= 80) return "Normal";
  if (score >= 60) return "Warning";
  return "Critical";
}

function CircularMetric({ label, value, colorClass }) {
  const percent = clamp(value ?? 0, 0, 100);

  return (
    <div className="iot-metric-card">
      <div
        className={`iot-circle ${colorClass}`}
        style={{ "--progress": `${percent}%` }}
      >
        <span>{percent}%</span>
      </div>
      <h3>{label}</h3>
    </div>
  );
}

function ThermometerMetric({ value }) {
  const percent = clamp(toPercent(value ?? 0, 0, 50), 0, 100);

  return (
    <div className="iot-metric-card">
      <div className="iot-thermometer">
        <div className="iot-thermometer-fill" style={{ height: `${percent}%` }} />
      </div>
      <div className="iot-thermometer-value">{value ?? "--"}°C</div>
      <h3>Temperature</h3>
    </div>
  );
}

function SwitchMetric({ label, active, onToggle, loading }) {
  return (
    <div className="iot-metric-card">
      <h2 className="iot-switch-title">{label}</h2>
      <div className={`iot-switch-text ${active ? "on" : "off"}`}>
        {active ? "ON" : "OFF"}
      </div>

      <button
        className={`iot-switch ${active ? "active" : ""}`}
        onClick={onToggle}
        disabled={loading}
      >
        <div className="iot-switch-knob" />
      </button>
    </div>
  );
}

export default function IotVisualBoard({ latest, deviceState, onToggleLed, controlling })  {
  const score = getScore(latest);
  const status = getStatus(score);
  const brightnessPercent = clamp(toPercent(latest?.light ?? 0, 0, 1023), 0, 100);
  const humidityPercent = clamp(Math.round(latest?.humidity ?? 0), 0, 100);

  return (
    <div className="iot-visual-layout">
      <div className="iot-visual-top">
        <section className="card iot-overview-card">
          <div className="iot-score-box">{score}%</div>

          <p className="iot-score-status">
            Overall Score: <span className={`status-${status.toLowerCase()}`}>{status}</span>
          </p>

          <div className="iot-ideal-range">
            <h3>Ideal levels for these 3 parameters:</h3>
            <p>Temperature: <strong>21 - 32°C</strong></p>
            <p>Humidity: <strong>40 - 80%</strong></p>
            <p>Brightness: <strong>60 - 100%</strong></p>
          </div>
        </section>

        <section className="card iot-device-card">
          <h2>Thiết bị hiện tại</h2>
          <p><strong>Device ID:</strong> {latest?.device_id || "--"}</p>
          <p><strong>Timestamp:</strong> {latest?.timestamp || "--"}</p>
          <p><strong>Gas:</strong> {latest?.gas ?? "--"}</p>
          <p><strong>Flame:</strong> {latest?.flame ?? "--"}</p>
        </section>
      </div>

      <div className="iot-visual-bottom">
        <ThermometerMetric value={latest?.temperature} />
        <CircularMetric label="Humidity" value={humidityPercent} colorClass="green" />
        <CircularMetric label="Brightness" value={brightnessPercent} colorClass="lime" />
        <SwitchMetric
  label="LED"
  active={Boolean(deviceState?.led)}
  onToggle={onToggleLed}
  loading={controlling}/>
      </div>
    </div>
  );
}