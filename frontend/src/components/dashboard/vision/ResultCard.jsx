import { toAssetUrl } from "../../../services/visionApi";

export default function ResultCard({ detectResult, videoResult }) {
  const hasImageResult = Boolean(detectResult);
  const hasVideoResult = Boolean(videoResult);

  return (
    <section className="card">
      <div className="card-header">
        <h2><span className="title-icon">🎯</span>Kết quả phát hiện</h2>
        <span className="tag pink">Detection</span>
      </div>

      {!hasImageResult && !hasVideoResult ? (
        <div className="empty-box">
          <div className="empty-icon">📦</div>
          <p>Chưa có kết quả nhận diện</p>
        </div>
      ) : (
        <>
          {hasImageResult ? (
            <>
              <div className="image-box framed-image">
                {detectResult.annotated_image_url ? (
                  <img src={toAssetUrl(detectResult.annotated_image_url)} alt="annotated" className="preview-image" />
                ) : (
                  <div className="empty-box">
                    <div className="empty-icon">🧭</div>
                    <p>Chưa có ảnh bounding box</p>
                  </div>
                )}
              </div>

              <div className="result-stats">
                <div className="mini-stat"><span>Model</span><strong>{detectResult.model_name || "--"}</strong></div>
                <div className="mini-stat"><span>Số object</span><strong>{detectResult.object_count ?? 0}</strong></div>
                <div className="mini-stat"><span>Danger</span><strong>{detectResult.danger_detected ? "Có" : "Không"}</strong></div>
              </div>

              <div className="soft-note"><strong>Version:</strong> {detectResult.model_version || "--"}</div>

              <div className="table-box">
                <table>
                  <thead>
                    <tr><th>Đối tượng</th><th>Độ tin cậy</th><th>BBox</th></tr>
                  </thead>
                  <tbody>
                    {(detectResult.detections || []).map((item, index) => (
                      <tr key={index}>
                        <td>{item.label || "Unknown"}</td>
                        <td>{item.confidence != null ? `${(item.confidence * 100).toFixed(2)}%` : "--"}</td>
                        <td>{item.bbox ? `${item.bbox.x1}, ${item.bbox.y1}, ${item.bbox.x2}, ${item.bbox.y2}` : "--"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : null}

          {hasVideoResult ? (
            <>
              <div className="result-stats">
                <div className="mini-stat"><span>Model</span><strong>{videoResult.model_name || "--"}</strong></div>
                <div className="mini-stat"><span>Alert frames</span><strong>{videoResult.alert_frame_count ?? 0}</strong></div>
                <div className="mini-stat"><span>Max confidence</span><strong>{videoResult.max_confidence ?? 0}</strong></div>
              </div>

              <div className="soft-note"><strong>Version:</strong> {videoResult.model_version || "--"}</div>

              <h3 className="subheading">Preview frames</h3>
              <div className="thumb-grid">
                {(videoResult.preview_images || []).map((url, idx) => (
                  <img key={idx} className="thumb" src={toAssetUrl(url)} alt={`preview-${idx}`} />
                ))}
              </div>

              <h3 className="subheading">Sampled events</h3>
              <div className="json-box">
                <pre>{JSON.stringify(videoResult.sampled_events || [], null, 2)}</pre>
              </div>
            </>
          ) : null}
        </>
      )}
    </section>
  );
}
