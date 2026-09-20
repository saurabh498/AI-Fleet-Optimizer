import { useState } from "react";

function EditShipmentModal({ shipment, onClose, onSave }) {
  const [formData, setFormData] = useState({
    pickup_city: shipment.pickup_city ?? "",
    pickup_latitude: shipment.pickup_latitude ?? "",
    pickup_longitude: shipment.pickup_longitude ?? "",
    destination_city: shipment.destination_city ?? "",
    destination_latitude: shipment.destination_latitude ?? "",
    destination_longitude: shipment.destination_longitude ?? "",
    weight: shipment.weight ?? "",
    volume: shipment.volume ?? "",
    cargo_type: shipment.cargo_type ?? "General",
    revenue: shipment.revenue ?? "",
    status: shipment.status ?? "available",
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

    if (!formData.pickup_city.trim()) {
      setError("Pickup city is required.");
      return;
    }
    if (!formData.destination_city.trim()) {
      setError("Destination city is required.");
      return;
    }
    if (!formData.weight || Number(formData.weight) <= 0) {
      setError("Weight must be greater than 0.");
      return;
    }
    if (!formData.revenue || Number(formData.revenue) <= 0) {
      setError("Revenue must be greater than 0.");
      return;
    }

    setSaving(true);
    try {
      await onSave({
        pickup_city: formData.pickup_city.trim(),
        pickup_latitude:
          formData.pickup_latitude === ""
            ? null
            : Number(formData.pickup_latitude),
        pickup_longitude:
          formData.pickup_longitude === ""
            ? null
            : Number(formData.pickup_longitude),
        destination_city: formData.destination_city.trim(),
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
          formData.volume === "" ? null : Number(formData.volume),
        cargo_type: formData.cargo_type,
        revenue: Number(formData.revenue),
        status: formData.status,
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update shipment.");
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
      <div
        className="modal-card shipment-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="dashboard-label">SHIPMENT MANAGEMENT</p>
            <h2>Edit Shipment #{shipment.load_id}</h2>
            <p>Update load details</p>
          </div>
          <button className="modal-close" onClick={onClose} disabled={saving}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-section-title">Route Information</div>

          <div className="form-grid">
            <div className="form-group">
              <label>Pickup City *</label>
              <input
                type="text"
                name="pickup_city"
                value={formData.pickup_city}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Destination City *</label>
              <input
                type="text"
                name="destination_city"
                value={formData.destination_city}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Pickup Latitude</label>
              <input
                type="number"
                name="pickup_latitude"
                value={formData.pickup_latitude}
                onChange={handleChange}
                step="any"
              />
            </div>

            <div className="form-group">
              <label>Pickup Longitude</label>
              <input
                type="number"
                name="pickup_longitude"
                value={formData.pickup_longitude}
                onChange={handleChange}
                step="any"
              />
            </div>

            <div className="form-group">
              <label>Destination Latitude</label>
              <input
                type="number"
                name="destination_latitude"
                value={formData.destination_latitude}
                onChange={handleChange}
                step="any"
              />
            </div>

            <div className="form-group">
              <label>Destination Longitude</label>
              <input
                type="number"
                name="destination_longitude"
                value={formData.destination_longitude}
                onChange={handleChange}
                step="any"
              />
            </div>
          </div>

          <div className="form-section-title">Load Information</div>

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
              />
            </div>

            <div className="form-group">
              <label>Cargo Type</label>
              <select
                name="cargo_type"
                value={formData.cargo_type}
                onChange={handleChange}
              >
                <option value="General">General</option>
                <option value="Electronics">Electronics</option>
                <option value="Textiles">Textiles</option>
                <option value="FMCG">FMCG</option>
                <option value="Machinery">Machinery</option>
                <option value="Pharma">Pharma</option>
                <option value="Food Grains">Food Grains</option>
                <option value="Auto Parts">Auto Parts</option>
                <option value="Chemicals">Chemicals</option>
                <option value="Other">Other</option>
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
                <option value="delivered">Delivered</option>
              </select>
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

export default EditShipmentModal;
