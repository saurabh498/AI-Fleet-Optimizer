import { useState } from "react";


const STATUSES = [
  "available",
  "on_duty",
  "resting",
  "off_duty",
  "inactive",
];


function DriverModal({ driver, trucks, onClose, onSave }) {
  const isEdit = Boolean(driver);
  const title = isEdit
    ? "Edit Driver #" + driver.driver_id
    : "Add New Driver";

  const [formData, setFormData] = useState({
    display_name: driver?.display_name ?? "",
    availability_status: driver?.availability_status ?? "available",
    assigned_truck_id: driver?.assigned_truck_id ?? "",
    accumulated_driving_minutes:
      driver?.accumulated_driving_minutes ?? 0,
    accumulated_since_last_rest_minutes:
      driver?.accumulated_since_last_rest_minutes ?? 0,
    rest_required: driver?.rest_required ?? false,
  });

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!formData.display_name.trim()) {
      setError("Display name is required.");
      return;
    }

    const payload = {
      display_name: formData.display_name.trim(),
      availability_status: formData.availability_status,
      assigned_truck_id:
        formData.assigned_truck_id === ""
          ? null
          : Number(formData.assigned_truck_id),
      accumulated_driving_minutes:
        Number(formData.accumulated_driving_minutes) || 0,
      accumulated_since_last_rest_minutes:
        Number(formData.accumulated_since_last_rest_minutes) || 0,
      rest_required: formData.rest_required,
    };

    setSaving(true);
    try {
      await onSave(payload);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        (isEdit ? "Failed to update driver." : "Failed to create driver.")
      );
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
        className="modal-card"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="dashboard-label">DRIVER MANAGEMENT</p>
            <h2>{title}</h2>
            <p>
              {isEdit
                ? "Update driver details"
                : "Register a driver for the fleet"}
            </p>
          </div>
          <button
            className="modal-close"
            onClick={onClose}
            disabled={saving}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Display Name *</label>
              <input
                type="text"
                name="display_name"
                value={formData.display_name}
                onChange={handleChange}
                placeholder="e.g. Ravi Kumar"
              />
            </div>

            <div className="form-group">
              <label>Availability</label>
              <select
                name="availability_status"
                value={formData.availability_status}
                onChange={handleChange}
              >
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Assigned Truck</label>
              <select
                name="assigned_truck_id"
                value={formData.assigned_truck_id}
                onChange={handleChange}
              >
                <option value="">— unassigned —</option>
                {trucks.map((t) => (
                  <option key={t.truck_id} value={t.truck_id}>
                    #{t.truck_id} · {t.truck_type} · {t.current_city || "?"}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Driving Minutes (daily total)</label>
              <input
                type="number"
                name="accumulated_driving_minutes"
                value={formData.accumulated_driving_minutes}
                onChange={handleChange}
                min="0"
              />
            </div>

            <div className="form-group">
              <label>Minutes Since Last Rest</label>
              <input
                type="number"
                name="accumulated_since_last_rest_minutes"
                value={formData.accumulated_since_last_rest_minutes}
                onChange={handleChange}
                min="0"
              />
            </div>

            <div className="form-group">
              <label>Rest Required</label>
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  name="rest_required"
                  checked={formData.rest_required}
                  onChange={handleChange}
                />
                <span>Flag driver as needing rest</span>
              </label>
            </div>
          </div>

          <div className="form-note">
            ⚠ Driving-hour rules are <strong>not legally verified</strong>.
            All driver checks are flagged for manager review.
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
            <button
              type="submit"
              className="primary-button"
              disabled={saving}
            >
              {saving ? "Saving..." : (isEdit ? "Save Changes" : "Create Driver")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}


export default DriverModal;
