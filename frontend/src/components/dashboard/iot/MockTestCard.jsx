export default function MockTestCard() {
  return (
    <section className="card">
      <div className="card-header">
        <h2><span className="title-icon">🧪</span>Mock Test IoT</h2>
        <span className="tag brown">Seed</span>
      </div>

      <div className="soft-note">
        Chạy lệnh này trong thư mục <strong>backend</strong> để tạo dữ liệu giả:
      </div>

      <div className="json-box">
        <pre>python -m app.seed_sensors</pre>
      </div>

      <div className="soft-note">
        Sau khi chạy seed, refresh lại IoT Dashboard để thấy dữ liệu mới trong DB.
      </div>
    </section>
  );
}