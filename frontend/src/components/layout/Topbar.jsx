export default function Topbar({ title, subtitle }) {
  return (
    <header className="dashboard-topbar">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
    </header>
  );
}
