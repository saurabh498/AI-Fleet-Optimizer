import { useState } from "react";


function SearchBriefModal({ brief, onClose }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(brief.generated_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Copy failed:", error);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([brief.generated_text], {
      type: "text/plain;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "search-brief-truck-" + brief.truck_id + ".txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const recommended = brief.external_search_recommended;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-card search-brief-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="dashboard-label">EXTERNAL SEARCH BRIEF</p>
            <h2>Truck #{brief.truck_id}</h2>
            <p>
              {recommended
                ? "No suitable internal shipment found. Copy this into an external load board."
                : "An internal match exists, but you can also try an external load board."}
            </p>
          </div>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className={"brief-badge " + (recommended ? "warn" : "info")}>
          {recommended
            ? "⚠ External search recommended"
            : "ℹ Internal search already returned matches"}
        </div>

        <div className="search-brief-meta">
          <div>
            <span>Generated at</span>
            <strong>{brief.generated_at}</strong>
          </div>
          <div>
            <span>Candidates evaluated</span>
            <strong>
              {brief.internal_search_summary.candidates_considered}
            </strong>
          </div>
          <div>
            <span>Feasible matches</span>
            <strong>
              {brief.internal_search_summary.feasible_matches}
            </strong>
          </div>
        </div>

        <pre className="search-brief-text">{brief.generated_text}</pre>

        <div className="brief-privacy-note">
          ⚠ {brief.privacy_note}
        </div>

        <div className="modal-actions">
          <button
            className="secondary-button"
            onClick={handleDownload}
          >
            Download .txt
          </button>
          <button
            className="primary-button"
            onClick={handleCopy}
          >
            {copied ? "Copied ✓" : "Copy to clipboard"}
          </button>
        </div>
      </div>
    </div>
  );
}


export default SearchBriefModal;
