import { useEffect, useState } from "react";
import { createTruck, getTrucks } from "../services/api";

function Trucks() {
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [formData, setFormData] = useState({
    truck_type: "Heavy",
    capacity: "",
    current_load: "0",
    current_latitude: "",
    current_longitude: "",
    current_city: "",
    status: "available",
    destination: "",
    cost_per_km: "",
  });

  const loadTrucks = async () => {
    try {
      setLoading(true);
      const data = await getTrucks();
      setTrucks(data);
    } catch (error) {
      console.error("Failed to load trucks:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrucks();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const resetForm = () => {
    setFormData({
      truck_type: "Heavy",
      capacity: "",
      current_load: "0",
      current_latitude: "",
      current_longitude: "",
      current_city: "",
      status: "available",
      destination: "",
      cost_per_km: "",
    });

    setFormError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setFormError("");
    setSuccessMessage("");

    if (!formData.truck_type.trim()) {
      setFormError("Truck type is required.");
      return;
    }

    if (!formData.capacity || Number(formData.capacity) <= 0) {
      setFormError("Capacity must be greater than 0.");
      return;
    }

    if (Number(formData.current_load) < 0) {
      setFormError("Current load cannot be negative.");
      return;
    }

    if (
      Number(formData.current_load) >
      Number(formData.capacity)
    ) {
      setFormError("Current load cannot exceed truck capacity.");
      return;
    }

    if (!formData.current_city.trim()) {
      setFormError("Current city is required.");
      return;
    }

    if (!formData.cost_per_km || Number(formData.cost_per_km) <= 0) {
      setFormError("Cost per km must be greater than 0.");
      return;
    }

    try {
      setSaving(true);

      const truckData = {
        truck_type: formData.truck_type.trim(),
        capacity: Number(formData.capacity),
        current_load: Number(formData.current_load),
        current_latitude:
          formData.current_latitude === ""
            ? null
            : Number(formData.current_latitude),
        current_longitude:
          formData.current_longitude === ""
            ? null
            : Number(formData.current_longitude),
        current_city: formData.current_city.trim(),
        status: formData.status,
        destination:
          formData.destination.trim() === ""
            ? null
            : formData.destination.trim(),
        cost_per_km: Number(formData.cost_per_km),
      };

      await createTruck(truckData);

      await loadTrucks();

      setShowForm(false);
      resetForm();
      setSuccessMessage("Truck added successfully.");

      setTimeout(() => {
        setSuccessMessage("");
      }, 3000);
    } catch (error) {
      console.error("Failed to create truck:", error);

      const message =
        error.response?.data?.detail ||
        "Failed to create truck. Please try again.";

      setFormError(message);
    } finally {
      setSaving(false);
    }
  };

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
          {successMessage && (
            <div className="success-message">
              ✓ {successMessage}
            </div>
          )}

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

              <button
                className="primary-button"
                onClick={() => {
                  resetForm();
                  setShowForm(true);
                }}
              >
                + Add Truck
              </button>
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

      {/* ADD TRUCK MODAL */}

      {showForm && (
        <div
          className="modal-overlay"
          onClick={() => {
            if (!saving) {
              setShowForm(false);
            }
          }}
        >
          <div
            className="modal-card"
            onClick={(event) => event.stopPropagation()}
          >

            <div className="modal-header">
              <div>
                <p className="dashboard-label">
                  FLEET MANAGEMENT
                </p>

                <h2>Add New Truck</h2>

                <p>
                  Register a vehicle into the fleet.
                </p>
              </div>

              <button
                className="modal-close"
                onClick={() => setShowForm(false)}
                disabled={saving}
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit}>

              <div className="form-grid">

                <div className="form-group">
                  <label>Truck Type *</label>

                  <select
                    name="truck_type"
                    value={formData.truck_type}
                    onChange={handleChange}
                  >
                    <option value="Heavy">Heavy</option>
                    <option value="Medium">Medium</option>
                    <option value="Light">Light</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Capacity (kg) *</label>

                  <input
                    type="number"
                    name="capacity"
                    value={formData.capacity}
                    onChange={handleChange}
                    min="1"
                    placeholder="e.g. 15000"
                  />
                </div>

                <div className="form-group">
                  <label>Current Load (kg)</label>

                  <input
                    type="number"
                    name="current_load"
                    value={formData.current_load}
                    onChange={handleChange}
                    min="0"
                    placeholder="0"
                  />
                </div>

                <div className="form-group">
                  <label>Current City *</label>

                  <input
                    type="text"
                    name="current_city"
                    value={formData.current_city}
                    onChange={handleChange}
                    placeholder="e.g. Mumbai"
                  />
                </div>

                <div className="form-group">
                  <label>Latitude</label>

                  <input
                    type="number"
                    name="current_latitude"
                    value={formData.current_latitude}
                    onChange={handleChange}
                    step="any"
                    placeholder="e.g. 19.076"
                  />
                </div>

                <div className="form-group">
                  <label>Longitude</label>

                  <input
                    type="number"
                    name="current_longitude"
                    value={formData.current_longitude}
                    onChange={handleChange}
                    step="any"
                    placeholder="e.g. 72.8777"
                  />
                </div>

                <div className="form-group">
                  <label>Status</label>

                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                  >
                    <option value="available">Available</option>
                    <option value="waiting">Waiting</option>
                    <option value="in_transit">In Transit</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Destination</label>

                  <input
                    type="text"
                    name="destination"
                    value={formData.destination}
                    onChange={handleChange}
                    placeholder="e.g. Pune"
                  />
                </div>

                <div className="form-group form-full">
                  <label>Operating Cost (₹ / km) *</label>

                  <input
                    type="number"
                    name="cost_per_km"
                    value={formData.cost_per_km}
                    onChange={handleChange}
                    min="0.01"
                    step="0.01"
                    placeholder="e.g. 25"
                  />
                </div>

              </div>

              {formError && (
                <div className="form-error">
                  ⚠ {formError}
                </div>
              )}

              <div className="modal-actions">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowForm(false)}
                  disabled={saving}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={saving}
                >
                  {saving ? "Creating..." : "Create Truck"}
                </button>

              </div>

            </form>

          </div>
        </div>
      )}

    </div>
  );
}

export default Trucks;