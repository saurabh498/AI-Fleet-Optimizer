import { useEffect, useState } from "react";
import { getShipments } from "../services/api";

function Shipments() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadShipments = async () => {
      try {
        const data = await getShipments();
        setShipments(data);
      } catch (error) {
        console.error("Failed to load shipments:", error);
      } finally {
        setLoading(false);
      }
    };

    loadShipments();
  }, []);

  const totalShipments = shipments.length;

  const availableShipments = shipments.filter(
    (shipment) => shipment.status === "available"
  ).length;

  const assignedShipments = shipments.filter(
    (shipment) => shipment.status === "assigned"
  ).length;

  const deliveredShipments = shipments.filter(
    (shipment) => shipment.status === "delivered"
  ).length;

  return (
    <div className="dashboard">

      <header className="dashboard-header">
        <div>
          <p className="dashboard-label">
            AI FLEET OPTIMIZER
          </p>

          <h1>Shipments</h1>

          <p className="dashboard-subtitle">
            Manage and monitor shipment loads
          </p>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>

      {loading ? (
        <div className="loading">
          Loading shipments...
        </div>
      ) : (
        <>
          {/* SHIPMENT KPIs */}

          <section className="kpi-grid">

            <div className="kpi-card">
              <div className="kpi-icon">📦</div>

              <div className="kpi-content">
                <p className="kpi-title">
                  Total Shipments
                </p>

                <h2 className="kpi-value">
                  {totalShipments}
                </h2>

                <p className="kpi-description">
                  All shipment loads
                </p>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-icon">🟢</div>

              <div className="kpi-content">
                <p className="kpi-title">
                  Available
                </p>

                <h2 className="kpi-value">
                  {availableShipments}
                </h2>

                <p className="kpi-description">
                  Ready for assignment
                </p>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-icon">📋</div>

              <div className="kpi-content">
                <p className="kpi-title">
                  Assigned
                </p>

                <h2 className="kpi-value">
                  {assignedShipments}
                </h2>

                <p className="kpi-description">
                  Currently assigned
                </p>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-icon">✅</div>

              <div className="kpi-content">
                <p className="kpi-title">
                  Delivered
                </p>

                <h2 className="kpi-value">
                  {deliveredShipments}
                </h2>

                <p className="kpi-description">
                  Successfully delivered
                </p>
              </div>
            </div>

          </section>

          {/* SHIPMENT TABLE */}

          <section className="dashboard-section">

            <div className="section-header">
              <div>
                <h2>Shipment Loads</h2>

                <p>
                  Current and completed shipment operations
                </p>
              </div>
            </div>

            <div className="shipment-table">

              <div className="table-header shipment-header">
                <span>Load</span>
                <span>Pickup</span>
                <span>Destination</span>
                <span>Weight</span>
                <span>Cargo</span>
                <span>Revenue</span>
                <span>Status</span>
              </div>

              {shipments.map((shipment) => (
                <div
                  className="table-row shipment-row"
                  key={shipment.load_id}
                >

                  <span>
                    <strong>
                      Load #{shipment.load_id}
                    </strong>
                  </span>

                  <span>
                    {shipment.pickup_city || "Unknown"}
                  </span>

                  <span>
                    {shipment.destination_city || "Unknown"}
                  </span>

                  <span>
                    {shipment.weight || 0} kg
                  </span>

                  <span>
                    {shipment.cargo_type || "—"}
                  </span>

                  <span>
                    ₹
                    {Number(
                      shipment.revenue || 0
                    ).toLocaleString("en-IN")}
                  </span>

                  <span
                    className={
                      "shipment-status " +
                      String(shipment.status || "")
                        .toLowerCase()
                        .replace(/\s+/g, "-")
                    }
                  >
                    {shipment.status || "Unknown"}
                  </span>

                </div>
              ))}

            </div>

          </section>
        </>
      )}

    </div>
  );
}

export default Shipments;