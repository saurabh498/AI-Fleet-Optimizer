import { useEffect, useState } from "react";
import {
  getTrucks,
  getShipments,
  getTruckDecision,
} from "../services/api";

import KpiCard from "../components/KpiCard";
import AIRecommendation from "../components/AIRecommendation";
import FleetMap from "../components/FleetMap";
import FleetStatus from "../components/FleetStatus";

function Dashboard() {
  const [trucks, setTrucks] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
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

        const decisionResults = await Promise.all(
          truckData.map(async (truck) => {
            try {
              return await getTruckDecision(truck.truck_id);
            } catch (error) {
              console.error(
                `Failed to load decision for Truck #${truck.truck_id}:`,
                error
              );
              return null;
            }
          })
        );

        setRecommendations(decisionResults.filter(Boolean));
      } catch (error) {
        console.error("Failed to load fleet data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadFleetData();
  }, []);

  const totalTrucks = trucks.length;
  const availableTrucks = trucks.filter((t) => t.status === "available").length;
  const assignedTrucks = trucks.filter((t) => t.status === "assigned").length;
  const inTransitTrucks = trucks.filter((t) => t.status === "in_transit").length;
  const waitingTrucks = trucks.filter((t) => t.status === "waiting").length;

  const totalShipments = shipments.length;
  const availableShipments = shipments.filter((s) => s.status === "available").length;
  const assignedShipments = shipments.filter((s) => s.status === "assigned").length;

  // Environmental + cost aggregation from live decisions
  const totalCo2 = recommendations.reduce((sum, r) => {
    const co2 = r?.best_match?.co2_kg;
    return sum + (co2 ? Number(co2) : 0);
  }, 0);

  const totalRouteCost = recommendations.reduce((sum, r) => {
    const cost = r?.best_match?.estimated_route_cost;
    return sum + (cost ? Number(cost) : 0);
  }, 0);

  const totalRouteDistance = recommendations.reduce((sum, r) => {
    const d = r?.best_match?.route?.total_distance_km;
    return sum + (d ? Number(d) : 0);
  }, 0);

  const recommendationsWithCo2 = recommendations.filter(
    (r) => r?.best_match?.co2_kg != null
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
            <KpiCard title="Total Trucks" value={totalTrucks} icon="🚛" description="Registered fleet" />
            <KpiCard title="Available" value={availableTrucks} icon="🟢" description="Ready for assignment" />
            <KpiCard title="Assigned" value={assignedTrucks} icon="📋" description="Currently assigned" />
            <KpiCard title="In Transit" value={inTransitTrucks} icon="🚚" description="Currently transporting" />
            <KpiCard title="Waiting" value={waitingTrucks} icon="⏳" description="Waiting for loads" />
          </section>

          {/* Environmental & cost impact of AI recommendations */}
          {recommendationsWithCo2 > 0 && (
            <section className="dashboard-section environmental-section">
              <div className="section-header">
                <div>
                  <h2>Environmental & Cost Impact</h2>
                  <p>
                    Aggregate footprint of AI-recommended backhauls
                    across the fleet
                  </p>
                </div>
                <span className="section-live-pill">
                  Live · {recommendationsWithCo2} recommendation
                  {recommendationsWithCo2 === 1 ? "" : "s"}
                </span>
              </div>

              <div className="kpi-grid">
                <KpiCard
                  title="Total CO₂"
                  value={`${totalCo2.toFixed(0)} kg`}
                  icon="🌱"
                  description="Estimated across recommended routes"
                />
                <KpiCard
                  title="Route Cost"
                  value={`₹${totalRouteCost.toLocaleString("en-IN", {
                    maximumFractionDigits: 0,
                  })}`}
                  icon="💸"
                  description="Fuel + driver + toll + maintenance"
                />
                <KpiCard
                  title="Route Distance"
                  value={`${totalRouteDistance.toFixed(0)} km`}
                  icon="🛣️"
                  description="Real road distance via OSRM"
                />
                <KpiCard
                  title="CO₂ / Route"
                  value={
                    recommendationsWithCo2 > 0
                      ? `${(totalCo2 / recommendationsWithCo2).toFixed(1)} kg`
                      : "—"
                  }
                  icon="📊"
                  description="Average per recommendation"
                />
              </div>
            </section>
          )}

          <section className="dashboard-section">
            <div className="section-header">
              <div>
                <h2>Shipment Overview</h2>
                <p>Current shipment and backhaul load status</p>
              </div>
            </div>

            <div className="kpi-grid shipment-kpis">
              <KpiCard title="Total Shipments" value={totalShipments} icon="📦" description="All shipments" />
              <KpiCard title="Available Loads" value={availableShipments} icon="🟢" description="Ready for assignment" />
              <KpiCard title="Assigned Loads" value={assignedShipments} icon="📋" description="Currently assigned" />
            </div>

            <div className="shipment-table">
              <div className="table-header shipment-header">
                <span>Load</span>
                <span>Pickup</span>
                <span>Destination</span>
                <span>Weight</span>
                <span>Revenue</span>
                <span>Status</span>
              </div>

              {shipments.map((shipment) => (
                <div className="table-row shipment-row" key={shipment.load_id}>
                  <span><strong>Load #{shipment.load_id}</strong></span>
                  <span>{shipment.pickup_city || "Unknown"}</span>
                  <span>{shipment.destination_city || "Unknown"}</span>
                  <span>{shipment.weight || 0} kg</span>
                  <span>₹{Number(shipment.revenue || 0).toLocaleString("en-IN")}</span>
                  <span className={`shipment-status ${String(shipment.status || "").toLowerCase()}`}>
                    {shipment.status || "Unknown"}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-header">
              <div>
                <h2>AI Recommendations</h2>
                <p>AI-powered backhaul assignment and waiting decisions</p>
              </div>
              <span className="section-live-pill">Live decision layer</span>
            </div>

            <div className="ai-recommendations-grid">
              {recommendations.length === 0 ? (
                <div className="no-recommendations">No AI recommendations available.</div>
              ) : (
                recommendations.map((rec) => (
                  <AIRecommendation key={rec.truck_id} recommendation={rec} />
                ))
              )}
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-header">
              <div>
                <h2>Live Fleet Map</h2>
                <p>Current GPS coordinates and operational truck state</p>
              </div>
              <div className="map-live-status">
                <span className="status-dot"></span>
                GPS Simulation Ready
              </div>
            </div>
            <FleetMap trucks={trucks} />
          </section>

          <section className="dashboard-section">
            <FleetStatus trucks={trucks} />
          </section>

          <section className="dashboard-section">
            <div className="section-header">
              <div>
                <h2>Fleet Overview</h2>
                <p>Current truck state, location and assignment context</p>
              </div>
            </div>

            <div className="truck-table">
              <div className="table-header">
                <span>Truck</span>
                <span>Type</span>
                <span>Capacity / Load</span>
                <span>Location</span>
                <span>Destination</span>
                <span>Status</span>
              </div>

              {trucks.map((truck) => (
                <div className="table-row fleet-overview-row" key={truck.truck_id}>
                  <span><strong>Truck #{truck.truck_id}</strong></span>
                  <span>{truck.truck_type}</span>
                  <span>{truck.current_load || 0} / {truck.capacity} kg</span>
                  <span>
                    <strong>{truck.current_city || "Unknown"}</strong>
                    <small className="fleet-coordinates">
                      {truck.current_latitude != null && truck.current_longitude != null
                        ? `${Number(truck.current_latitude).toFixed(4)}, ${Number(truck.current_longitude).toFixed(4)}`
                        : "GPS unavailable"}
                    </small>
                  </span>
                  <span>{truck.destination || "—"}</span>
                  <span className={`truck-status ${truck.status}`}>
                    {String(truck.status || "Unknown").replaceAll("_", " ")}
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
