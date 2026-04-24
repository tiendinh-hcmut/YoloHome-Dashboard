import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const from = location.state?.from?.pathname || "/";

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(form.username, form.password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err?.response?.data?.detail || "Đăng nhập thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <div className="auth-brand">
          <p className="auth-kicker">YOLOHOME</p>
          <h1>Đăng nhập hệ thống</h1>
          <p>Đăng nhập để truy cập dashboard theo quyền: admin, operator hoặc viewer.</p>
        </div>
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="username">Tên đăng nhập</label>
            <input id="username" name="username" type="text" value={form.username} onChange={handleChange} placeholder="Nhập username" required />
          </div>
          <div className="field">
            <label htmlFor="password">Mật khẩu</label>
            <input id="password" name="password" type="password" value={form.password} onChange={handleChange} placeholder="Nhập mật khẩu" required />
          </div>
          {error ? <div className="auth-error">{error}</div> : null}
          <button className="primary-btn full-width" type="submit" disabled={loading}>
            {loading ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>
        </form>
      </div>
    </div>
  );
}
