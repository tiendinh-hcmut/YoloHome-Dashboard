export default function MediaLabCard({
  videoRef,
  canvasRef,
  selectedVideo,
  loadingDetect,
  cameraOn,
  autoDetect,
  onVideoChange,
  onDetectVideo,
  onStartCamera,
  onStopCamera,
  onCaptureOnce,
  onToggleAutoDetect,
}) {
  return (
    <section className="card">
      <div className="card-header">
        <h2><span className="title-icon">🎥</span>Video & Webcam</h2>
        <span className="tag purple">Stream</span>
      </div>

      <div className="media-lab-grid">
        <div className="media-block">
          <h3 className="subheading">Upload video</h3>
          <div className="upload-box">
            <input type="file" accept="video/*" onChange={onVideoChange} />
            <button className="primary-btn" onClick={onDetectVideo} disabled={loadingDetect}>
              {loadingDetect ? "Đang xử lý..." : "Phát hiện video"}
            </button>
          </div>
          <div className="soft-note">
            {selectedVideo ? `Đã chọn: ${selectedVideo.name}` : "Chưa chọn video"}
          </div>
        </div>

        <div className="media-block">
          <h3 className="subheading">Webcam local</h3>
          <div className="webcam-toolbar">
            <button className="success-btn" onClick={onStartCamera}>Mở camera</button>
            <button className="danger-btn" onClick={onStopCamera}>Tắt camera</button>
            <button className="primary-btn" onClick={onCaptureOnce}>Chụp 1 frame</button>
            <button className="warning-btn" onClick={onToggleAutoDetect}>
              {autoDetect ? "Dừng auto detect" : "Auto detect 1s"}
            </button>
          </div>

          <div className="image-box framed-image webcam-frame">
            <video ref={videoRef} autoPlay playsInline muted className="preview-image" />
            <canvas ref={canvasRef} style={{ display: "none" }} />
          </div>

          <div className="camera-state-row">
            <span className={`state-badge ${cameraOn ? "active" : ""}`}>Camera: {cameraOn ? "ON" : "OFF"}</span>
            <span className={`state-badge ${autoDetect ? "active" : ""}`}>Auto detect: {autoDetect ? "ON" : "OFF"}</span>
          </div>
        </div>
      </div>
    </section>
  );
}
