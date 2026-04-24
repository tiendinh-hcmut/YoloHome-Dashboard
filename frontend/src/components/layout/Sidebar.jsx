export default function Sidebar({ user, activeTab, onChangeTab, onLogout }) {
  const allowedTabs = user?.allowed_dashboards || [];

  const menu = [
    { key: "vision", label: "Vision Dashboard" },
    { key: "iot", label: "IoT Dashboard" },
  ].filter((item) => allowedTabs.includes(item.key));

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <p className="auth-kicker">YOLOHOME</p>
        <h2>Control Panel</h2>
      </div>

      <div className="sidebar-user">
        <strong>{user?.full_name || user?.username}</strong>
        <span>{user?.role}</span>
      </div>

      <nav className="sidebar-menu">
        {menu.map((item) => (
          <button key={item.key} className={`sidebar-link ${activeTab === item.key ? "active" : ""}`} onClick={() => onChangeTab(item.key)}>
            {item.label}
          </button>
        ))}
      </nav>

      <button className="danger-btn full-width" onClick={onLogout}>Đăng xuất</button>
    </aside>
  );
}
