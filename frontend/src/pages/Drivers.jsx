import { useEffect, useState } from "react";

import {
  getDrivers,
  getTrucks,
  createDriver,
  updateDriver,
  deleteDriver,
  markRestTaken,
} from "../services/api";
import RoleGate from "../components/RoleGate";
import ConfirmDialog from "../components/ConfirmDialog";
import DriverModal from "../components/DriverModal";


function Drivers() {
  const [drivers, setDrivers] = useState([]);
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showForm, setShowForm] = useState(false);
  const [editingDriver, setEditingDriver] = useState(null);
  const [deletingDriver, setDeletingDriver] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [driverData, truckData] = await Promise.all([
        getDrivers(),
        getTrucks(),
      ]);
      setDrivers(driverData);
      setTrucks(truckData);
    } catch (error) {
      console.error("Failed to load drivers:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const flash = (msg) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  const handleCreate = async (payload) => {
    await createDriver(payload);
    await loadData();
    setShowForm(false);
    flash("Driver added successfully.");
  };

  const handleUpdate = async (payload) => {
    await updateDriver(editingDriver.driver_id, payload);
    await loadData();
    setEditingDriver(null);
    flash("Driver updated successfully.");
  };

  const handleDelete = async () => {
    setDeleteLoading(true);
    setDeleteError("");
    try {
      await deleteDriver(deletingDriver.driver_id);
      await loadData();
      setDeletingDriver(null);
      flash("Driver deleted successfully.");
    } catch (error) {
      setDeleteError(
        error.response?.data?.detail || "Failed to delete driver."
      );
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleMarkRest = async (driver) => {
    try {
      await markRestTaken(driver.driver_id);
      await loadData();
      flash("Rest recorded for " + driver.display_name + ".");
    } catch (error) {
      console.error("Failed to mark rest:", error);
    }
  };

  const truckLabel = (id) => {
    if (id == null) return "—";
    const t = trucks.find((x) => x.truck_id === id);
    return t ? "#" + t.truck_id + " · " + (t.current_city || "?") : "#" + id;
  };

  const availableCount = drivers.filter(
    (d) => d.availability_status === "available"
  ).length;
  const onDutyCount = drivers.filter(
    (d) => d.availability_status === "on_duty"
  ).length;
  const restCount = drivers.filter((d) => d.rest_required).length;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-label">AI FLEET OPTIMIZER</p>
          <h1>Drivers</h1>
          <p className="dashboard-subtitle">
            Manage driver availability, hours, and truck assignments
          </p>
        </div>
        <div className="system-status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>

      {loading ? (
        <div className="loading">Loading drivers...</div>
      ) : (
        <>
          {successMessage && (
            <div className="success-message">✓ {successMessage}</div>
          )}

          <section className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-icon">🧑‍✈️</div>
              <div className="kpi-content">
                <p className="kpi-title">Total Drivers</p>
                <h2 className="kpi-value">{drivers.length}</h2>
                <p className="kpi-description">Registered drivers</p>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">🟢</div>
              <div className="kpi-content">
                <p className="kpi-title">Available</p>
                <h2 className="kpi-value">{availableCount}</h2>
                <p className="kpi-description">Ready for assignment</p>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">🚚</div>
              <div className="kpi-content">
                <p className="kpi-title">On Duty</p>
                <h2 className="kpi-value">{onDutyCount}</h2>
                <p className="kpi-description">Currently working</p>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">🛑</div>
              <div className="kpi-content">
                <p className="kpi-title">Rest Required</p>
                <h2 className="kpi-value">{restCount}</h2>
                <p className="kpi-description">Flagged for rest</p>
              </div>
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-header">
              <div>
                <h2>Driver Roster</h2>
                <p>Availability, hours, and assignments</p>
              </div>
              <RoleGate allow={["manager", "admin"]}>
                <button
                  className="primary-button"
                  onClick={() => setShowForm(true)}
                >
                  + Add Driver
                </button>
              </RoleGate>
            </div>

            <div className="driver-table">
              <div className="table-header driver-header">
                <span>Driver</span>
                <span>Status</span>
                <span>Truck</span>
                <span>Daily Min</span>
                <span>Since Rest</span>
                <span>Rest?</span>
                <span>Actions</span>
              </div>

              {drivers.length === 0 && (
                <div className="table-empty">
                  No drivers registered yet.
                </div>
              )}

              {drivers.map((d) => (
                <div className="table-row driver-row" key={d.driver_id}>
                  <span>
                    <strong>{d.display_name}</strong>
                    <small className="row-subnote">#{d.driver_id}</small>
                  </span>
                  <span
                    className={
                      "truck-status " +
                      String(d.availability_status || "")
                        .toLowerCase()
                        .replace(/\s+/g, "-")
                    }
                  >
                    {String(d.availability_status || "?").replace(/_/g, " ")}
                  </span>
                  <span>{truckLabel(d.assigned_truck_id)}</span>
                  <span>{d.accumulated_driving_minutes} min</span>
                  <span>{d.accumulated_since_last_rest_minutes} min</span>
                  <span className={d.rest_required ? "rest-yes" : "rest-no"}>
                    {d.rest_required ? "⚠ Yes" : "No"}
                  </span>
                  <RoleGate allow={["manager", "admin"]}>
                    <div className="row-actions">
                      {d.rest_required && (
                        <button
                          className="row-action-btn"
                          title="Mark rest taken"
                          onClick={() => handleMarkRest(d)}
                        >
                          ✅
                        </button>
                      )}
                      <button
                        className="row-action-btn"
                        title="Edit driver"
                        onClick={() => setEditingDriver(d)}
                      >
                        ✏
                      </button>
                      <button
                        className="row-action-btn delete"
                        title="Delete driver"
                        onClick={() => {
                          setDeletingDriver(d);
                          setDeleteError("");
                        }}
                      >
                        🗑
                      </button>
                    </div>
                  </RoleGate>
                </div>
              ))}
            </div>

            <div className="form-note">
              ⚠ Driving-hour rules are configured in{" "}
              <code>config/driver_rules.yaml</code> and are{" "}
              <strong>not legally verified</strong>. All feasibility passes
              require manager review.
            </div>
          </section>
        </>
      )}

      {showForm && (
        <DriverModal
          trucks={trucks}
          onClose={() => setShowForm(false)}
          onSave={handleCreate}
        />
      )}

      {editingDriver && (
        <DriverModal
          driver={editingDriver}
          trucks={trucks}
          onClose={() => setEditingDriver(null)}
          onSave={handleUpdate}
        />
      )}

      <ConfirmDialog
        open={Boolean(deletingDriver)}
        title="Delete this driver?"
        message={
          deletingDriver
            ? deletingDriver.display_name + " (driver #" + deletingDriver.driver_id + ") will be permanently removed."
            : ""
        }
        error={deleteError}
        confirmLabel="Delete"
        danger
        loading={deleteLoading}
        onConfirm={handleDelete}
        onCancel={() => {
          setDeletingDriver(null);
          setDeleteError("");
        }}
      />
    </div>
  );
}


export default Drivers;
