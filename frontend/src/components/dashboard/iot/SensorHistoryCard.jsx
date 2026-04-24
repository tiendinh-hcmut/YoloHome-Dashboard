export default function SensorHistoryCard({ history }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2><span className="title-icon">🗂️</span>Lịch sử dữ liệu IoT</h2>
        <span className="tag purple">History</span>
      </div>

      {!history?.length ? (
        <div className="empty-box">
          <div className="empty-icon">📘</div>
          <p>Chưa có dữ liệu lịch sử</p>
        </div>
      ) : (
        <div className="table-box">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Device</th>
                <th>Temp</th>
                <th>Humidity</th>
                <th>Gas</th>
                <th>Light</th>
                <th>Flame</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id}>
                  <td>{item.timestamp}</td>
                  <td>{item.device_id}</td>
                  <td>{item.temperature ?? "--"}</td>
                  <td>{item.humidity ?? "--"}</td>
                  <td>{item.gas ?? "--"}</td>
                  <td>{item.light ?? "--"}</td>
                  <td>{item.flame ?? "--"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}