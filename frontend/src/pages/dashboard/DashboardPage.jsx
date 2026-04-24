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
import { detectFrame, detectImage, detectVideo, getHealth } from "../../services/visionApi";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const allowed = user?.allowed_dashboards || ["vision"];
  const [activeTab, setActiveTab] = useState(allowed[0] || "vision");

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const timerRef = useRef(null);

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

  useEffect(() => {
    fetchHealth();
    return () => {
      stopCamera();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  useEffect(() => {
    if (!autoDetect) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    timerRef.current = setInterval(async () => {
      const blob = await captureFrameBlob();
      if (!blob) return;
      try {
        const res = await detectFrame(blob);
        setDetectResult(res);
        setVideoResult(null);
      } catch (err) {
        console.error(err);
      }
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [autoDetect]);

  const fetchHealth = async () => {
    try {
      const data = await getHealth();
      setHealth(data);
    } catch (err) {
      setError("Không kết nối được backend.");
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraOn(true);
    } catch (err) {
      alert("Không mở được webcam.");
    }
  };

  const stopCamera = () => {
    const video = videoRef.current;
    if (video?.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
      video.srcObject = null;
    }
    setCameraOn(false);
    setAutoDetect(false);
  };

  const captureFrameBlob = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.videoWidth === 0) return null;
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
    if (!selectedImage) return alert("Chọn ảnh trước.");
    try {
      setLoadingDetect(true);
      const res = await detectImage(selectedImage);
      setDetectResult(res);
      setVideoResult(null);
    } catch (err) {
      alert("Detect ảnh thất bại.");
    } finally {
      setLoadingDetect(false);
    }
  };

  const handleDetectVideo = async () => {
    if (!selectedVideo) return alert("Chọn video trước.");
    try {
      setLoadingDetect(true);
      const res = await detectVideo(selectedVideo);
      setVideoResult(res);
      setDetectResult(null);
    } catch (err) {
      alert("Detect video thất bại.");
    } finally {
      setLoadingDetect(false);
    }
  };

  const handleCaptureOnce = async () => {
    const blob = await captureFrameBlob();
    if (!blob) return alert("Chưa có frame webcam.");
    try {
      setLoadingDetect(true);
      const res = await detectFrame(blob);
      setDetectResult(res);
      setVideoResult(null);
    } catch (err) {
      alert("Detect frame thất bại.");
    } finally {
      setLoadingDetect(false);
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
      <Sidebar user={user} activeTab={activeTab} onChangeTab={setActiveTab} onLogout={handleLogout} />
      <main className="dashboard-main">{renderContent()}</main>
    </div>
  );
}
