import { useEffect, useState } from "react";

import {
  getRestFacilities,
  importRestFacilitiesCsv,
  deleteRestFacility,
} from "../services/api";
import RoleGate from "../components/RoleGate";
import ConfirmDialog from "../components/ConfirmDialog";


function RestFacilities() {
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(true);

  const [csvName, setCsvName] = useState("");
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [importError, setImportError] = useState("");

  const [deletingFacility, setDeletingFacility] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadFacilities = async () => {
    try {
      setLoading(true);
      const data = await getRestFacilities();
      setFacilities(data);
    } catch (error) {
      console.error("Failed to load facilities:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFacilities();
  }, []);

  const flash = (msg) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  const handleImport = async (event) => {
    event.preventDefault();
    setImportError("");
    setImportResult(null);

    if (!csvName.trim()) {
      setImportError("Filename is required (e.g. nh48_2026-10.csv).");
      return;
    }

    setImporting(true);
    try {
      const result = await importRestFacilitiesCsv(csvName.trim());
      setImportResult(result);
      if (result.created > 0) {
        await loadFacilities();
        flash("Imported " + result.created + " facilit(y/ies).");
      }
    } catch (error) {
      setImportError(
        error.response?.data?.detail || "Failed to import CSV."
      );
    } finally {
      setImporting(false);
    }
  };

  const handleDelete = async () => {
    setDeleteLoading(true);
    setDeleteError("");
    try {
      await deleteRestFacility(deletingFacility.facility_id);
      await loadFacilities();
      setDeletingFacility(null);
      flash("Facility deleted.");
    } catch (error) {
      setDeleteError(
        error.response?.data?.detail || "Failed to delete facility."
      );
    } finally {
      setDeleteLoading(false);
    }
  };

  const verifiedCount = facilities.filter(
    (f) => f.verification_status === "verified"
  ).length;
  const pendingCount = facilities.filter(
    (f) => f.verification_status === "pending"
  ).length;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-label">AI FLEET OPTIMIZER</p>
          <h1>Rest Facilities</h1>
          <p className="dashboard-subtitle">
            Verified driver-rest facilities used by the decision engine
          </p>
        </div>
        <div className="system-status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>

      {loading ? (
        <div className="loading">Loading facilities...</div>
      ) : (
        <>
          {successMessage && (
            <div className="success-message">✓ {successMessage}</div>
          )}

          <section className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-icon">🏠</div>
              <div className="kpi-content">
                <p className="kpi-title">Total Facilities</p>
                <h2 className="kpi-value">{facilities.length}</h2>
                <p className="kpi-description">Imported and stored</p>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">✅</div>
              <div className="kpi-content">
                <p className="kpi-title">Verified</p>
                <h2 className="kpi-value">{verifiedCount}</h2>
                <p className="kpi-description">Used by decision engine</p>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">⏳</div>
              <div className="kpi-content">
                <p className="kpi-title">Pending Review</p>
                <h2 className="kpi-value">{pendingCount}</h2>
                <p className="kpi-description">Not yet trusted</p>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">📄</div>
              <div className="kpi-content">
                <p className="kpi-title">Importer</p>
                <h2 className="kpi-value">CSV</h2>
                <p className="kpi-description">Source URL required</p>
              </div>
            </div>
          </section>

          <RoleGate allow={["manager", "admin"]}>
            <section className="dashboard-section">
              <div className="section-header">
                <div>
                  <h2>Import Facilities</h2>
                  <p>
                    Place a CSV in <code>data/rest_facilities/</code> and enter its filename
                  </p>
                </div>
              </div>

              <form className="import-form" onSubmit={handleImport}>
                <input
                  type="text"
                  value={csvName}
                  onChange={(e) => setCsvName(e.target.value)}
                  placeholder="e.g. nh48_2026-10.csv"
                  disabled={importing}
                />
                <button
                  type="submit"
                  className="primary-button"
                  disabled={importing}
                >
                  {importing ? "Importing..." : "Import CSV"}
                </button>
              </form>

              {importError && (
                <div className="form-error">⚠ {importError}</div>
              )}

              {importResult && (
                <div className="import-result">
                  <div>
                    <strong>File:</strong> {importResult.file}
                  </div>
                  <div>
                    <strong>Rows:</strong> {importResult.total_rows} · <strong>Created:</strong> {importResult.created} · <strong>Skipped:</strong> {importResult.skipped_duplicates}
                  </div>
                  {importResult.rejected?.length > 0 && (
                    <div className="import-rejected">
                      <strong>Rejected rows:</strong>
                      <ul>
                        {importResult.rejected.map((r, i) => (
                          <li key={i}>
                            Row {r.row}: {r.reason}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </section>
          </RoleGate>

          <section className="dashboard-section">
            <div className="section-header">
              <div>
                <h2>Facility Directory</h2>
                <p>Only verified rows are used by the decision engine</p>
              </div>
            </div>

            <div className="facility-table">
              <div className="table-header facility-header">
                <span>Facility</span>
                <span>Type</span>
                <span>Location</span>
                <span>Road</span>
                <span>Status</span>
                <span>Source</span>
                <span>Actions</span>
              </div>

              {facilities.length === 0 && (
                <div className="table-empty">
                  No facilities imported yet.
                </div>
              )}

              {facilities.map((f) => (
                <div className="table-row facility-row" key={f.facility_id}>
                  <span>
                    <strong>{f.name}</strong>
                    <small className="row-subnote">#{f.facility_id}</small>
                  </span>
                  <span>{f.facility_type.replace(/_/g, " ")}</span>
                  <span>
                    {f.latitude.toFixed(3)}, {f.longitude.toFixed(3)}
                  </span>
                  <span>{f.road_reference || "—"}</span>
                  <span className={"facility-status " + f.verification_status}>
                    {f.verification_status}
                  </span>
                  <span>
                    <a
                      href={f.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="source-link"
                    >
                      link ↗
                    </a>
                    <small className="row-subnote">{f.source_date}</small>
                  </span>
                  <RoleGate allow={["manager", "admin"]}>
                    <div className="row-actions">
                      <button
                        className="row-action-btn delete"
                        title="Delete facility"
                        onClick={() => {
                          setDeletingFacility(f);
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
              ⚠ Facilities require a documented <code>source_url</code> and{" "}
              <code>source_date</code>. The importer rejects rows without
              them. Live availability (parking spaces, dormitory beds) is{" "}
              <strong>not modelled</strong> — no source provides it.
            </div>
          </section>
        </>
      )}

      <ConfirmDialog
        open={Boolean(deletingFacility)}
        title="Delete this facility?"
        message={
          deletingFacility
            ? deletingFacility.name + " will be removed from the directory."
            : ""
        }
        error={deleteError}
        confirmLabel="Delete"
        danger
        loading={deleteLoading}
        onConfirm={handleDelete}
        onCancel={() => {
          setDeletingFacility(null);
          setDeleteError("");
        }}
      />
    </div>
  );
}


export default RestFacilities;
