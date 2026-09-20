import { useState } from "react";

function EditTruckModal({ truck, onClose, onSave }) {
  const [formData, setFormData] = useState({
    truck_type: truck.truck_type || "HCV",
    capacity: truck.capacity ?? "",
    current_load: truck.current_load ?? 0,
    current_city: truck.current_city ?? "",
    current_latitude: truck.current_latitude ?? "",
    current_longitude: truck.current_longitude ?? "",
    status: truck.status || "available",
    destination: truck.destination ?? "",
    cost_per_km: truck.cost_per_km ?? "",
  });

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!formData.capacity || Number(formData.capacity) <= 0) {
      setError("Capacity must be greater than 0.");
      return;
    }
    if (!formData.current_city.trim()) {
      setError("Current city is required.");
      return;
    }
    if (!formData.cost_per_km || Number(formData.cost_per_km) <= 0) {
      setError("Cost per km must be greater than 0.");
      return;
    }

    setSaving(true);
    try {
      await onSave({
        truck_type: formData.truck_type,
        capacity: Number(formData.capacity),
        current_load: Number(formData.current_load) || 0,
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
          formData.destination.trim() === "" ? null : formData.destination.trim(),
        cost_per_km: Number(formData.cost_per_km),
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update truck.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="modal-overlay"
      onClick={() => {
        if (!saving) onClose();
      }}
    >
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <p className="dashboard-label">FLEET MANAGEMENT</p>
            <h2>Edit Truck #{truck.truck_id}</h2>
            <p>Update vehicle details</p>
          </div>
          <button className="modal-close" onClick={onClose} disabled={saving}>
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
                <option value="HCV">HCV — Heavy Commercial Vehicle</option>
                <option value="MCV">MCV — Medium Commercial Vehicle</option>
                <option value="LCV">LCV — Light Commercial Vehicle</option>
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
              />
            </div>

            <div className="form-group">
              <label>Current City *</label>
              <input
                type="text"
                name="current_city"
                value={formData.current_city}
                onChange={handleChange}
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
                <option value="assigned">Assigned</option>
                <option value="in_transit">In Transit</option>
                <option value="waiting">Waiting</option>
              </select>
            </div>

            <div className="form-group">
              <label>Destination</label>
              <input
                type="text"
                name="destination"
                value={formData.destination}
                onChange={handleChange}
                placeholder="Optional"
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
              />
            </div>
          </div>

          {error && <div className="form-error">⚠ {error}</div>}

          <div className="modal-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={onClose}
              disabled={saving}
            >
              Cancel
            </button>
            <button type="submit" className="primary-button" disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditTruckModal;
