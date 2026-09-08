import { useEffect, useState } from "react";
import { getTrucks } from "../services/api";

function Trucks() {
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTrucks = async () => {
      try {
        const data = await getTrucks();
        setTrucks(data);
      } catch (error) {
        console.error("Failed to load trucks:", error);
      } finally {
        setLoading(false);
      }
    };

    loadTrucks();
  }, []);

  const totalTrucks = trucks.length;

  const availableTrucks = trucks.filter(
    (truck) => truck.status === "available"
  ).length;

  const inTransitTrucks = trucks.filter(
    (truck) => truck.status === "in_transit"
  ).length;

  const waitingTrucks = trucks.filter(
    (truck) => truck.status === "waiting"
  ).length;

  return (
    <div className="dashboard">

      <header className="dashboard-header">
        <div>
          <p className="dashboard-label">
            AI FLEET OPTIMIZER
          </p>

          <h1>Trucks</h1>

          <p className="dashboard-subtitle">
            Manage and monitor registered fleet vehicles
          </p>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>

      {loading ? (
        <div className="loading">
          Loading trucks...
        </div>
      ) : (
        <>
          {/* TRUCK KPIs */}

          <section className="kpi-grid">

            <div className="kpi-card">
              <div className="kpi-icon">🚛</div>

              <div className="kpi-content">
                <p className="kpi-title">
                  Total Trucks
                </p>

                <h2 className="kpi-value">
                  {totalTrucks}
                </h2>

                <p className="kpi-description">
                  Registered fleet
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
                  {availableTrucks}
                </h2>

                <p className="kpi-description">
                  Ready for assignment
                </p>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-icon">🚚</div>

              <div className="kpi-content">
                <p className="kpi-title">
                  In Transit
                </p>

                <h2 className="kpi-value">
                  {inTransitTrucks}
                </h2>

                <p className="kpi-description">
                  Currently transporting
                </p>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-icon">⏳</div>

              <div className="kpi-content">
                <p className="kpi-title">
                  Waiting
                </p>

                <h2 className="kpi-value">
                  {waitingTrucks}
                </h2>

                <p className="kpi-description">
                  Waiting for loads
                </p>
              </div>
            </div>

          </section>

          {/* TRUCK TABLE */}

          <section className="dashboard-section">

            <div className="section-header">
              <div>
                <h2>Fleet Vehicles</h2>

                <p>
                  Registered trucks and their current operational status
                </p>
              </div>
            </div>

            <div className="truck-table">

              <div className="table-header">
                <span>Truck</span>
                <span>Type</span>
                <span>Capacity</span>
                <span>Current Load</span>
                <span>Location</span>
                <span>Destination</span>
                <span>Status</span>
              </div>

              {trucks.map((truck) => (
                <div
                  className="table-row"
                  key={truck.truck_id}
                >

                  <span>
                    <strong>
                      🚛 Truck #{truck.truck_id}
                    </strong>
                  </span>

                  <span>
                    {truck.truck_type || "Unknown"}
                  </span>

                  <span>
                    {truck.capacity || 0} kg
                  </span>

                  <span>
                    {truck.current_load || 0} kg
                  </span>

                  <span>
                    {truck.current_city || "Unknown"}
                  </span>

                  <span>
                    {truck.destination || "—"}
                  </span>

                  <span
                    className={
                      "truck-status " +
                      String(truck.status || "")
                        .toLowerCase()
                        .replace(/\s+/g, "-")
                    }
                  >
                    {truck.status || "Unknown"}
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

export default Trucks;