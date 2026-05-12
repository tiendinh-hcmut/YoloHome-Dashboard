export default function SensorHistoryCard({ history }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2>🗂 Lịch sử dữ liệu IoT</h2>
        <span className="tag blue">History</span>
      </div>

      {!history || history.length === 0 ? (
        <div className="empty-box">
          <div className="empty-icon">📭</div>
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
                <th>Light</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item, index) => (
                <tr key={item._id || index}>
                  <td>{item.timestamp || "--"}</td>
                  <td>{item.device_id || item.metadata?.device_id || "--"}</td>
                  <td>{item.temperature ?? "--"}</td>
                  <td>{item.humidity ?? "--"}</td>
                  <td>{item.light ?? "--"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}