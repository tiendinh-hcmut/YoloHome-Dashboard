export default function UploadCard({ previewUrl, loadingDetect, onFileChange, onDetect }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2><span className="title-icon">📷</span>Khung nhận ảnh</h2>
        <span className="tag blue">Image</span>
      </div>

      <div className="upload-box">
        <input type="file" accept="image/*" onChange={onFileChange} />
        <button className="primary-btn" onClick={onDetect} disabled={loadingDetect}>
          {loadingDetect ? "Đang phát hiện..." : "Phát hiện ảnh"}
        </button>
      </div>

      <div className="image-box framed-image">
        {previewUrl ? (
          <img src={previewUrl} alt="preview" className="preview-image" />
        ) : (
          <div className="empty-box">
            <div className="empty-icon">🖼️</div>
            <p>Chưa có ảnh được chọn</p>
          </div>
        )}
      </div>
    </section>
  );
}
