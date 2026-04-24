export default function LatestSensorCard({ latest }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2><span className="title-icon">📡</span>Dữ liệu IoT mới nhất</h2>
        <span className="tag blue">Latest</span>
      </div>

      {!latest ? (
        <div className="empty-box">
          <div className="empty-icon">📭</div>
          <p>Chưa có dữ liệu từ IoT trong database</p>
        </div>
      ) : (
        <>
          <div className="result-stats">
            <div className="mini-stat">
              <span>Device ID</span>
              <strong>{latest.device_id || "--"}</strong>
            </div>
            <div className="mini-stat">
              <span>Nhiệt độ</span>
              <strong>{latest.temperature ?? "--"} °C</strong>
            </div>
            <div className="mini-stat">
              <span>Độ ẩm</span>
              <strong>{latest.humidity ?? "--"} %</strong>
            </div>
          </div>

          <div className="result-stats">
            <div className="mini-stat">
              <span>Gas</span>
              <strong>{latest.gas ?? "--"}</strong>
            </div>
            <div className="mini-stat">
              <span>Ánh sáng</span>
              <strong>{latest.light ?? "--"}</strong>
            </div>
            <div className="mini-stat">
              <span>Flame</span>
              <strong>{latest.flame ?? "--"}</strong>
            </div>
          </div>

          <div className="result-stats">
            <div className="mini-stat">
              <span>Relay</span>
              <strong>{String(latest.relay_status ?? false)}</strong>
            </div>
            <div className="mini-stat">
              <span>Buzzer</span>
              <strong>{String(latest.buzzer_status ?? false)}</strong>
            </div>
            <div className="mini-stat">
              <span>LED</span>
              <strong>{String(latest.led_status ?? false)}</strong>
            </div>
          </div>

          <div className="soft-note">
            <strong>Timestamp:</strong> {latest.timestamp || "--"}
          </div>
        </>
      )}
    </section>
  );
}