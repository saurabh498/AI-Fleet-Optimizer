function ConfirmDialog({
  open,
  title = "Are you sure?",
  message,
  error,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  danger = false,
  loading = false,
  onConfirm,
  onCancel,
}) {
  if (!open) return null;

  return (
    <div
      className="modal-overlay"
      onClick={() => {
        if (!loading) onCancel();
      }}
    >
      <div
        className="modal-card confirm-card"
        onClick={(event) => event.stopPropagation()}
      >
        <div className={`confirm-icon ${danger ? "danger" : ""}`}>
          {danger ? "⚠" : "?"}
        </div>

        <h2>{title}</h2>

        {message && <p className="confirm-message">{message}</p>}

        {error && (
          <div className="confirm-error">
            <span>⚠</span>
            {error}
          </div>
        )}

        <div className="modal-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </button>

          <button
            type="button"
            className={danger ? "danger-button" : "primary-button"}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "Working..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
