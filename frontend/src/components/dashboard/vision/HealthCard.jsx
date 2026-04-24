export default function HealthCard({ health }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2><span className="title-icon">🩺</span>Trạng thái hệ thống</h2>
        <span className="tag brown">Health</span>
      </div>

      <div className="health-grid">
        <div className="mini-stat">
          <span>API</span>
          <strong>{health?.status || "checking..."}</strong>
        </div>
        <div className="mini-stat">
          <span>Database</span>
          <strong>{health?.database || "--"}</strong>
        </div>
        <div className="mini-stat">
          <span>Model</span>
          <strong>{health?.model_name || "--"}</strong>
        </div>
      </div>

      <div className="soft-note"><strong>Version:</strong> {health?.model_version || "--"}</div>
      <div className="soft-note"><strong>Time:</strong> {health?.time || "--"}</div>
    </section>
  );
}
