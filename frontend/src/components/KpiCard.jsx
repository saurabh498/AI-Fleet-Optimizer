function KpiCard({ title, value, icon, description }) {
  return (
    <div className="kpi-card">
      <div className="kpi-icon">{icon}</div>

      <div className="kpi-content">
        <p className="kpi-title">{title}</p>
        <h2 className="kpi-value">{value}</h2>
        <p className="kpi-description">{description}</p>
      </div>
    </div>
  );
}

export default KpiCard;