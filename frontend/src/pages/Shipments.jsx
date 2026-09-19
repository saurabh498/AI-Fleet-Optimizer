import { useEffect, useState } from "react";
import { createShipment, getShipments } from "../services/api";
import RoleGate from "../components/RoleGate";

function Shipments() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [formData, setFormData] = useState({
    pickup_city: "",
    pickup_latitude: "",
    pickup_longitude: "",
    destination_city: "",
    destination_latitude: "",
    destination_longitude: "",
    weight: "",
    volume: "",
    cargo_type: "General",
    pickup_start: "",
    pickup_deadline: "",
    delivery_deadline: "",
    revenue: "",
    status: "available",
  });

  const loadShipments = async () => {
    try {
      setLoading(true);
      const data = await getShipments();
      setShipments(data);
    } catch (error) {
      console.error("Failed to load shipments:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadShipments();
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
      pickup_city: "",
      pickup_latitude: "",
      pickup_longitude: "",
      destination_city: "",
      destination_latitude: "",
      destination_longitude: "",
      weight: "",
      volume: "",
      cargo_type: "General",
      pickup_start: "",
      pickup_deadline: "",
      delivery_deadline: "",
      revenue: "",
      status: "available",
    });

    setFormError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setFormError("");
    setSuccessMessage("");

    if (!formData.pickup_city.trim()) {
      setFormError("Pickup city is required.");
      return;
    }

    if (!formData.destination_city.trim()) {
      setFormError("Destination city is required.");
      return;
    }

    if (!formData.weight || Number(formData.weight) <= 0) {
      setFormError("Shipment weight must be greater than 0.");
      return;
    }

    if (!formData.cargo_type.trim()) {
      setFormError("Cargo type is required.");
      return;
    }

    if (!formData.revenue || Number(formData.revenue) <= 0) {
      setFormError("Revenue must be greater than 0.");
      return;
    }

    try {
      setSaving(true);

      const shipmentData = {
        pickup_city: formData.pickup_city.trim(),

        pickup_latitude:
          formData.pickup_latitude === ""
            ? null
            : Number(formData.pickup_latitude),

        pickup_longitude:
          formData.pickup_longitude === ""
            ? null
            : Number(formData.pickup_longitude),

        destination_city:
          formData.destination_city.trim(),

        destination_latitude:
          formData.destination_latitude === ""
            ? null
            : Number(formData.destination_latitude),

        destination_longitude:
          formData.destination_longitude === ""
            ? null
            : Number(formData.destination_longitude),

        weight: Number(formData.weight),

        volume:
          formData.volume === ""
            ? null
            : Number(formData.volume),

        cargo_type: formData.cargo_type.trim(),

        pickup_start:
          formData.pickup_start === ""
            ? null
            : new Date(formData.pickup_start).toISOString(),

        pickup_deadline:
          formData.pickup_deadline === ""
            ? null
            : new Date(formData.pickup_deadline).toISOString(),

        delivery_deadline:
          formData.delivery_deadline === ""
            ? null
            : new Date(formData.delivery_deadline).toISOString(),

        revenue: Number(formData.revenue),

        status: formData.status,
      };

      await createShipment(shipmentData);

      await loadShipments();

      setShowForm(false);
      resetForm();

      setSuccessMessage(
        "Shipment added successfully."
      );

      setTimeout(() => {
        setSuccessMessage("");
      }, 3000);
    } catch (error) {
      console.error(
        "Failed to create shipment:",
        error
      );

      const message =
        error.response?.data?.detail ||
        "Failed to create shipment. Please try again.";

      setFormError(message);
    } finally {
      setSaving(false);
    }
  };

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
          {successMessage && (
            <div className="success-message">
              ✓ {successMessage}
            </div>
          )}

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

              <RoleGate allow={["manager", "admin"]}>
                <button
                  className="primary-button"
                  onClick={() => {
                    resetForm();
                    setShowForm(true);
                  }}
                >
                  + Add Shipment
                </button>
              </RoleGate>
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

      {/* ADD SHIPMENT MODAL */}

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
            className="modal-card shipment-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            <div className="modal-header">
              <div>
                <p className="dashboard-label">
                  SHIPMENT MANAGEMENT
                </p>

                <h2>Add New Shipment</h2>

                <p>
                  Register a new load for the AI
                  matching engine.
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

              <div className="form-section-title">
                Route Information
              </div>

              <div className="form-grid">

                <div className="form-group">
                  <label>Pickup City *</label>

                  <input
                    type="text"
                    name="pickup_city"
                    value={formData.pickup_city}
                    onChange={handleChange}
                    placeholder="e.g. Mumbai"
                  />
                </div>

                <div className="form-group">
                  <label>Destination City *</label>

                  <input
                    type="text"
                    name="destination_city"
                    value={
                      formData.destination_city
                    }
                    onChange={handleChange}
                    placeholder="e.g. Pune"
                  />
                </div>

                <div className="form-group">
                  <label>Pickup Latitude</label>

                  <input
                    type="number"
                    name="pickup_latitude"
                    value={
                      formData.pickup_latitude
                    }
                    onChange={handleChange}
                    step="any"
                    placeholder="19.076"
                  />
                </div>

                <div className="form-group">
                  <label>Pickup Longitude</label>

                  <input
                    type="number"
                    name="pickup_longitude"
                    value={
                      formData.pickup_longitude
                    }
                    onChange={handleChange}
                    step="any"
                    placeholder="72.8777"
                  />
                </div>

                <div className="form-group">
                  <label>
                    Destination Latitude
                  </label>

                  <input
                    type="number"
                    name="destination_latitude"
                    value={
                      formData.destination_latitude
                    }
                    onChange={handleChange}
                    step="any"
                    placeholder="18.5204"
                  />
                </div>

                <div className="form-group">
                  <label>
                    Destination Longitude
                  </label>

                  <input
                    type="number"
                    name="destination_longitude"
                    value={
                      formData.destination_longitude
                    }
                    onChange={handleChange}
                    step="any"
                    placeholder="73.8567"
                  />
                </div>

              </div>

              <div className="form-section-title">
                Load Information
              </div>

              <div className="form-grid">

                <div className="form-group">
                  <label>Weight (kg) *</label>

                  <input
                    type="number"
                    name="weight"
                    value={formData.weight}
                    onChange={handleChange}
                    min="1"
                    step="0.01"
                    placeholder="e.g. 5000"
                  />
                </div>

                <div className="form-group">
                  <label>Volume</label>

                  <input
                    type="number"
                    name="volume"
                    value={formData.volume}
                    onChange={handleChange}
                    min="0"
                    step="0.01"
                    placeholder="e.g. 15"
                  />
                </div>

                <div className="form-group">
                  <label>Cargo Type *</label>

                  <select
                    name="cargo_type"
                    value={formData.cargo_type}
                    onChange={handleChange}
                  >
                    <option value="General">
                      General
                    </option>

                    <option value="Electronics">
                      Electronics
                    </option>

                    <option value="Food">
                      Food
                    </option>

                    <option value="Industrial">
                      Industrial
                    </option>

                    <option value="Automotive">
                      Automotive
                    </option>

                    <option value="Other">
                      Other
                    </option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Revenue (₹) *</label>

                  <input
                    type="number"
                    name="revenue"
                    value={formData.revenue}
                    onChange={handleChange}
                    min="1"
                    step="0.01"
                    placeholder="e.g. 30000"
                  />
                </div>

                <div className="form-group">
                  <label>Status</label>

                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                  >
                    <option value="available">
                      Available
                    </option>

                    <option value="assigned">
                      Assigned
                    </option>
                  </select>
                </div>

              </div>

              <div className="form-section-title">
                Time Windows
              </div>

              <div className="form-grid">

                <div className="form-group">
                  <label>Pickup Start</label>

                  <input
                    type="datetime-local"
                    name="pickup_start"
                    value={
                      formData.pickup_start
                    }
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>Pickup Deadline</label>

                  <input
                    type="datetime-local"
                    name="pickup_deadline"
                    value={
                      formData.pickup_deadline
                    }
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group form-full">
                  <label>Delivery Deadline</label>

                  <input
                    type="datetime-local"
                    name="delivery_deadline"
                    value={
                      formData.delivery_deadline
                    }
                    onChange={handleChange}
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
                  {saving
                    ? "Creating..."
                    : "Create Shipment"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

    </div>
  );
}

export default Shipments;