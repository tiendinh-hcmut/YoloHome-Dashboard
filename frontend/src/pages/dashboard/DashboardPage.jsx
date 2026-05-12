import IotDashboard from "./IotDashboard";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Sidebar from "../../components/layout/Sidebar";
import Topbar from "../../components/layout/Topbar";
import HealthCard from "../../components/dashboard/vision/HealthCard";
import UploadCard from "../../components/dashboard/vision/UploadCard";
import MediaLabCard from "../../components/dashboard/vision/MediaLabCard";
import ResultCard from "../../components/dashboard/vision/ResultCard";
import {
  detectFrame,
  detectImage,
  detectVideo,
  getHealth,
} from "../../services/visionApi";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const allowed = user?.allowed_dashboards || ["vision"];
  const [activeTab, setActiveTab] = useState(allowed[0] || "vision");

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const timerRef = useRef(null);
  const detectingRef = useRef(false);

  const [health, setHealth] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [cameraOn, setCameraOn] = useState(false);
  const [autoDetect, setAutoDetect] = useState(false);
  const [detectResult, setDetectResult] = useState(null);
  const [videoResult, setVideoResult] = useState(null);
  const [loadingDetect, setLoadingDetect] = useState(false);
  const [error, setError] = useState("");
  const [liveStatus, setLiveStatus] = useState("Chưa bắt đầu autodetect");

  useEffect(() => {
    fetchHealth();

    return () => {
      stopCamera();
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!autoDetect || !cameraOn) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }

    runAutoDetectOnce();

    timerRef.current = setInterval(() => {
      runAutoDetectOnce();
    }, 2000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [autoDetect, cameraOn]);

  const fetchHealth = async () => {
    try {
      const data = await getHealth();
      setHealth(data);
    } catch (err) {
      console.error(err);
      setError("Không kết nối được backend.");
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setCameraOn(true);
      setLiveStatus("Webcam đã sẵn sàng");
    } catch (err) {
      console.error(err);
      alert("Không mở được webcam.");
    }
  };

  const stopCamera = () => {
    const video = videoRef.current;

    if (video?.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
      video.srcObject = null;
    }

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    setCameraOn(false);
    setAutoDetect(false);
    setLiveStatus("Đã tắt webcam");
  };

  const captureFrameBlob = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || video.videoWidth === 0 || video.videoHeight === 0) {
      return null;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.85);
    });
  };

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedImage(file);
    setImagePreview(URL.createObjectURL(file));
    setVideoResult(null);
  };

  const handleVideoChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedVideo(file);
    setDetectResult(null);
  };

  const handleDetectImage = async () => {
    if (!selectedImage) {
      alert("Chọn ảnh trước.");
      return;
    }

    try {
      setLoadingDetect(true);
      const res = await detectImage(selectedImage);
      setDetectResult(res);
      setVideoResult(null);

      const danger = Boolean(res?.danger_synced);
      const dangerFeed = res?.danger_feed_value ?? 0;
      const pumpFeed = res?.pump_feed_value ?? 0;
      const pumpCommand = res?.pump_command_sent ?? 0;

      setLiveStatus(
        `danger=${danger ? 1 : 0} | danger_feed=${dangerFeed} | pump_feed=${pumpFeed} | pump_command=${pumpCommand}`
      );
    } catch (err) {
      console.error(err);
      alert("Detect ảnh thất bại.");
    } finally {
      setLoadingDetect(false);
    }
  };

  const handleDetectVideo = async () => {
    if (!selectedVideo) {
      alert("Chọn video trước.");
      return;
    }

    try {
      setLoadingDetect(true);
      const res = await detectVideo(selectedVideo);
      setVideoResult(res);
      setDetectResult(null);

      const danger = Boolean(res?.danger_synced);
      const dangerFeed = res?.danger_feed_value ?? 0;
      const pumpFeed = res?.pump_feed_value ?? 0;
      const pumpCommand = res?.pump_command_sent ?? 0;

      setLiveStatus(
        `danger=${danger ? 1 : 0} | danger_feed=${dangerFeed} | pump_feed=${pumpFeed} | pump_command=${pumpCommand}`
      );
    } catch (err) {
      console.error(err);
      alert("Detect video thất bại.");
    } finally {
      setLoadingDetect(false);
    }
  };

  const handleCaptureOnce = async () => {
    const blob = await captureFrameBlob();
    if (!blob) {
      alert("Chưa có frame webcam.");
      return;
    }

    try {
      setLoadingDetect(true);
      const res = await detectFrame(blob);
      setDetectResult(res);
      setVideoResult(null);

      const danger = Boolean(res?.danger_synced);
      const dangerFeed = res?.danger_feed_value ?? 0;
      const pumpFeed = res?.pump_feed_value ?? 0;
      const pumpCommand = res?.pump_command_sent ?? 0;

      setLiveStatus(
        `danger=${danger ? 1 : 0} | danger_feed=${dangerFeed} | pump_feed=${pumpFeed} | pump_command=${pumpCommand}`
      );
    } catch (err) {
      console.error(err);
      alert("Detect frame thất bại.");
    } finally {
      setLoadingDetect(false);
    }
  };

  const runAutoDetectOnce = async () => {
    if (detectingRef.current) return;
    detectingRef.current = true;

    try {
      const blob = await captureFrameBlob();
      if (!blob) return;

      const res = await detectFrame(blob);
      setDetectResult(res);
      setVideoResult(null);

      const danger = Boolean(res?.danger_synced);
      const dangerFeed = res?.danger_feed_value ?? 0;
      const pumpFeed = res?.pump_feed_value ?? 0;
      const pumpCommand = res?.pump_command_sent ?? 0;

      setLiveStatus(
        `danger=${danger ? 1 : 0} | danger_feed=${dangerFeed} | pump_feed=${pumpFeed} | pump_command=${pumpCommand}`
      );
    } catch (err) {
      console.error(err);
      setLiveStatus("Autodetect lỗi");
    } finally {
      detectingRef.current = false;
    }
  };

  const renderContent = () => {
    if (activeTab === "iot") {
      return <IotDashboard />;
    }

    return (
      <>
        <Topbar
          title="Vision Dashboard"
          subtitle="Nhận diện cháy khói bằng ảnh, video và webcam."
        />

        {error ? <div className="global-error">{error}</div> : null}

        <section className="card" style={{ marginBottom: 16 }}>
          <div className="card-header">
            <h2>
              <span className="title-icon">📡</span>Auto Detect Status
            </h2>
            <span className="tag blue">Live</span>
          </div>
          <div className="soft-note">
            <strong>Backend publish:</strong> {liveStatus}
          </div>
        </section>

        <div className="dashboard-grid">
          <div className="dashboard-column">
            <HealthCard health={health} />
            <UploadCard
              previewUrl={imagePreview}
              loadingDetect={loadingDetect}
              onFileChange={handleImageChange}
              onDetect={handleDetectImage}
            />
          </div>

          <div className="dashboard-column dashboard-column--wide">
            <MediaLabCard
              videoRef={videoRef}
              canvasRef={canvasRef}
              selectedVideo={selectedVideo}
              loadingDetect={loadingDetect}
              cameraOn={cameraOn}
              autoDetect={autoDetect}
              onVideoChange={handleVideoChange}
              onDetectVideo={handleDetectVideo}
              onStartCamera={startCamera}
              onStopCamera={stopCamera}
              onCaptureOnce={handleCaptureOnce}
              onToggleAutoDetect={() => setAutoDetect((v) => !v)}
            />
            <ResultCard detectResult={detectResult} videoResult={videoResult} />
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="dashboard-shell">
      <Sidebar
        user={user}
        activeTab={activeTab}
        onChangeTab={setActiveTab}
        onLogout={handleLogout}
      />
      <main className="dashboard-main">{renderContent()}</main>
    </div>
  );
}