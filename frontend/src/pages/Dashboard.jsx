import { useEffect, useState } from "react";
import { getTrucks, getShipments } from "../services/api";
import KpiCard from "../components/KpiCard";

function Dashboard() {
  const [trucks, setTrucks] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFleetData = async () => {
      try {
        const [truckData, shipmentData] = await Promise.all([
          getTrucks(),
          getShipments(),
        ]);

        setTrucks(truckData);
        setShipments(shipmentData);
      } catch (error) {
        console.error("Failed to load fleet data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadFleetData();
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

  const totalShipments = shipments.length;

  const availableShipments = shipments.filter(
    (shipment) => shipment.status === "available"
  ).length;

  const assignedShipments = shipments.filter(
    (shipment) => shipment.status === "assigned"
  ).length;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-label">AI FLEET OPTIMIZER</p>
          <h1>Fleet Dashboard</h1>
          <p className="dashboard-subtitle">
            AI-based fleet monitoring and backhaul decision support
          </p>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>

      {loading ? (
        <div className="loading">Loading fleet data...</div>
      ) : (
        <>
          <section className="kpi-grid">
            <KpiCard
              title="Total Trucks"
              value={totalTrucks}
              icon="🚛"
              description="Registered fleet"
            />

            <KpiCard
              title="Available"
              value={availableTrucks}
              icon="🟢"
              description="Ready for assignment"
            />

            <KpiCard
              title="In Transit"
              value={inTransitTrucks}
              icon="🚚"
              description="Currently transporting"
            />

            <KpiCard
              title="Waiting"
              value={waitingTrucks}
              icon="⏳"
              description="Waiting for loads"
            />
          </section>

          <section className="dashboard-section">
            <div className="section-header">
              <div>
                <section className="dashboard-section">
                  <div className="section-header">
                    <div>
                      <h2>Shipment Overview</h2>
                      <p>Current shipment and backhaul load status</p>
                    </div>
                  </div>

                  <div className="kpi-grid shipment-kpis">
                    <KpiCard
                      title="Total Shipments"
                      value={totalShipments}
                      icon="📦"
                      description="All shipments"
                    />

                    <KpiCard
                      title="Available Loads"
                      value={availableShipments}
                      icon="🟢"
                      description="Ready for assignment"
                    />

                    <KpiCard
                      title="Assigned Loads"
                      value={assignedShipments}
                      icon="📋"
                      description="Currently assigned"
                    />
                  </div>
                </section>
                <h2>Fleet Overview</h2>
                <p>Current status of registered trucks</p>
              </div>
            </div>

            <div className="truck-table">
              <div className="table-header">
                <span>Truck</span>
                <span>Type</span>
                <span>Capacity</span>
                <span>Location</span>
                <span>Status</span>
              </div>

              {trucks.map((truck) => (
                <div className="table-row" key={truck.truck_id}>
                  <span>Truck #{truck.truck_id}</span>
                  <span>{truck.truck_type}</span>
                  <span>{truck.capacity} kg</span>
                  <span>{truck.current_city || "Unknown"}</span>
                  <span className={`truck-status ${truck.status}`}>
                    {truck.status}
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

export default Dashboard;