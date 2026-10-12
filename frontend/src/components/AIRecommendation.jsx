import { useState } from "react";
import { useNavigate } from "react-router-dom";

import RoleGate from "./RoleGate";
import SearchBriefModal from "./SearchBriefModal";
import api, { getSearchBrief } from "../services/api";


function AIRecommendation({ recommendation }) {
  const navigate = useNavigate();
  const [assigning, setAssigning] = useState(false);
  const [assignError, setAssignError] = useState("");
  const [briefLoading, setBriefLoading] = useState(false);
  const [brief, setBrief] = useState(null);
  const [briefError, setBriefError] = useState("");

  if (!recommendation) {
    return null;
  }

  const decision = recommendation.decision || "UNKNOWN";
  const decisionClass = decision.toLowerCase();

  const bestMatch = recommendation.best_match;
  const metrics = recommendation.decision_metrics;
  const mlExplanation = recommendation.ml_explanation;
  const mlContext = recommendation.ml_context;
  const shap = mlExplanation?.shap;
  const costBreakdown = bestMatch?.estimated_cost_breakdown;
  const driverFeasibility = recommendation.driver_feasibility;
  const restSuggestion = recommendation.rest_facility_suggestion;

  const canAssign =
    decision === "ASSIGN_NOW" || decision === "REVIEW";

  const handleAssignNow = async () => {
    if (!bestMatch) return;
    setAssigning(true);
    setAssignError("");

    try {
      const resp = await api.post(
        "/assignments/truck/" +
          recommendation.truck_id +
          "/load/" +
          bestMatch.load_id
      );
      const assignmentId = resp.data?.assignment?.assignment_id;

      if (assignmentId) {
        await api.put("/assignments/" + assignmentId + "/start");
      }

      navigate("/trucks");
    } catch (err) {
      setAssignError(
        err.response?.data?.detail || "Failed to assign shipment."
      );
    } finally {
      setAssigning(false);
    }
  };

  const handleOpenBrief = async () => {
    setBriefLoading(true);
    setBriefError("");
    try {
      const result = await getSearchBrief(recommendation.truck_id);
      setBrief(result);
    } catch (err) {
      setBriefError(
        err.response?.data?.detail ||
          "Failed to generate search brief."
      );
    } finally {
      setBriefLoading(false);
    }
  };

  return (
    <div className="ai-recommendation-card">
      <div className="ai-card-header">
        <div>
          <p className="ai-label">AI DECISION ENGINE</p>
          <h2>Truck #{recommendation.truck_id}</h2>
        </div>
        <span className={"decision-badge " + decisionClass}>
          {decision.replaceAll("_", " ")}
        </span>
      </div>

      <div className="ai-decision">
        <div className="ai-decision-icon">🤖</div>
        <div>
          <h3>{decision.replaceAll("_", " ")}</h3>
          <p>{recommendation.action}</p>
        </div>
      </div>

      <div className="ai-reason">
        <strong>AI Reason</strong>
        <p>{recommendation.reason}</p>
      </div>

      {bestMatch && (
        <div className="best-match">
          <div className="subsection-title">Best Backhaul Match</div>
          <div className="match-grid">
            <div>
              <span>Load</span>
              <strong>#{bestMatch.load_id}</strong>
            </div>
            <div>
              <span>Route</span>
              <strong>
                {bestMatch.pickup_city} → {bestMatch.destination_city}
              </strong>
              {bestMatch.distance_to_pickup_km != null && (
                <small className="match-subnote">
                  Pickup {Number(bestMatch.distance_to_pickup_km).toFixed(0)} km away
                </small>
              )}
            </div>
            <div>
              <span>Weight</span>
              <strong>{bestMatch.weight} kg</strong>
            </div>
            <div>
              <span>Revenue</span>
              <strong>
                ₹{Number(bestMatch.revenue || 0).toLocaleString("en-IN")}
              </strong>
            </div>
          </div>
        </div>
      )}

      {metrics && (
        <div className="ai-metrics">
          <div className="subsection-title">Decision Metrics</div>
          <div className="metrics-grid">
            <div className="metric">
              <span>Decision Score</span>
              <strong>{metrics.decision_score}</strong>
            </div>
            <div className="metric">
              <span>ML Adjustment</span>
              <strong>
                {metrics.ml_adjustment > 0
                  ? "+" + metrics.ml_adjustment
                  : metrics.ml_adjustment}
              </strong>
            </div>
            <div className="metric">
              <span>Route Efficiency</span>
              <strong>{metrics.route_efficiency_score}%</strong>
            </div>
            <div className="metric">
              <span>Estimated Profit</span>
              <strong>
                ₹{Number(metrics.estimated_route_profit || 0).toLocaleString("en-IN")}
              </strong>
            </div>
          </div>
        </div>
      )}

      {driverFeasibility && (
        <div
          className={
            "driver-panel " +
            (driverFeasibility.feasible ? "feasible" : "infeasible")
          }
        >
          <div className="subsection-title">Driver Feasibility</div>
          <div className="metrics-grid">
            <div className="metric">
              <span>Driver</span>
              <strong>{driverFeasibility.display_name}</strong>
            </div>
            <div className="metric">
              <span>Status</span>
              <strong>{driverFeasibility.availability_status}</strong>
            </div>
            <div className="metric">
              <span>Driving Minutes</span>
              <strong>{driverFeasibility.accumulated_driving_minutes}</strong>
            </div>
            <div className="metric">
              <span>Since Last Rest</span>
              <strong>
                {driverFeasibility.accumulated_since_last_rest_minutes} min
              </strong>
            </div>
            <div className="metric">
              <span>Trip Estimate</span>
              <strong>
                {driverFeasibility.estimated_trip_minutes} min
              </strong>
            </div>
            <div className="metric">
              <span>Feasible</span>
              <strong>
                {driverFeasibility.feasible === true
                  ? "Yes"
                  : driverFeasibility.feasible === false
                    ? "No"
                    : "Unknown"}
              </strong>
            </div>
          </div>
          <div className="driver-reason">
            <strong>Reason:</strong> {driverFeasibility.reason}
          </div>
          {driverFeasibility.rules_verified_against_law === false && (
            <div className="driver-unverified">
              ⚠ Driving-hour rules not verified against law — manual review required
            </div>
          )}
        </div>
      )}

      {restSuggestion && (
        <div className="rest-facility-panel">
          <div className="subsection-title">
            {restSuggestion.recommended_action_label
              ? restSuggestion.recommended_action_label.replace(/_/g, " ")
              : "Rest Facility Suggestion"}
          </div>

          {restSuggestion.facility ? (
            <>
              <div className="rest-facility-name">
                {restSuggestion.facility.name}
              </div>
              <div className="metrics-grid">
                <div className="metric">
                  <span>Type</span>
                  <strong>
                    {String(restSuggestion.facility.facility_type).replace(/_/g, " ")}
                  </strong>
                </div>
                <div className="metric">
                  <span>Distance</span>
                  <strong>{restSuggestion.facility.distance_km} km</strong>
                </div>
                <div className="metric">
                  <span>Duration</span>
                  <strong>{restSuggestion.facility.duration_min} min</strong>
                </div>
                <div className="metric">
                  <span>Distance Source</span>
                  <strong>{restSuggestion.facility.distance_source}</strong>
                </div>
              </div>
              <div className="driver-reason">
                <strong>Reason:</strong> {restSuggestion.reason}
              </div>
              {restSuggestion.facility.distance_source === "haversine" && (
                <div className="rest-facility-warning">
                  ⚠ Distance is a straight-line estimate — road routing unavailable
                </div>
              )}
            </>
          ) : (
            <div className="driver-reason">
              <strong>Reason:</strong> {restSuggestion.reason}
            </div>
          )}
        </div>
      )}

      {costBreakdown && (
        <div className="cost-breakdown">
          <div className="subsection-title">Cost Breakdown</div>
          <div className="metrics-grid">
            <div className="metric">
              <span>Fuel</span>
              <strong>
                ₹{Number(costBreakdown.fuel_cost || 0).toLocaleString("en-IN")}
              </strong>
            </div>
            <div className="metric">
              <span>Driver</span>
              <strong>
                ₹{Number(costBreakdown.driver_cost || 0).toLocaleString("en-IN")}
              </strong>
            </div>
            <div className="metric">
              <span>Toll</span>
              <strong>
                ₹{Number(costBreakdown.toll_cost || 0).toLocaleString("en-IN")}
              </strong>
            </div>
            <div className="metric">
              <span>Maintenance</span>
              <strong>
                ₹{Number(costBreakdown.maintenance_cost || 0).toLocaleString("en-IN")}
              </strong>
            </div>
          </div>
          <div className="cost-total">
            <span>
              Total · {costBreakdown.truck_class || "—"} ·{" "}
              {costBreakdown.mileage_km_per_litre || "?"} km/L
            </span>
            <strong>
              ₹{Number(costBreakdown.total_cost || 0).toLocaleString("en-IN")}
            </strong>
          </div>
        </div>
      )}

      {bestMatch?.co2_kg != null && (
        <div className="co2-impact">
          <div className="subsection-title">Environmental Impact</div>
          <div className="metrics-grid">
            <div className="metric">
              <span>CO₂ Emissions</span>
              <strong>{Number(bestMatch.co2_kg).toFixed(1)} kg</strong>
            </div>
            <div className="metric">
              <span>CO₂ / km</span>
              <strong>
                {Number(bestMatch.co2_per_km_kg || 0).toFixed(3)} kg/km
              </strong>
            </div>
          </div>
        </div>
      )}

      {mlContext?.available && (
        <div className="ml-context">
          <div className="subsection-title">ML Prediction</div>
          <div className="metrics-grid">
            <div className="metric">
              <span>Predicted Demand</span>
              <strong>{mlContext.predicted_demand}</strong>
            </div>
            <div className="metric">
              <span>Predicted Waiting</span>
              <strong>{mlContext.predicted_waiting_time} hrs</strong>
            </div>
            <div className="metric">
              <span>Demand Model</span>
              <strong>{mlContext.demand_model}</strong>
            </div>
            <div className="metric">
              <span>Waiting Model</span>
              <strong>{mlContext.waiting_model}</strong>
            </div>
          </div>
        </div>
      )}

      {mlExplanation && (
        <div
          className={
            "ml-explanation " +
            (mlExplanation.impact || "NEUTRAL").toLowerCase()
          }
        >
          <strong>ML Impact: {mlExplanation.impact}</strong>
          <p>{mlExplanation.reason}</p>
        </div>
      )}

      {shap?.summary && (
        <div className="shap-explanation">
          <div className="subsection-title">SHAP Explainability</div>
          <p className="shap-summary">{shap.summary}</p>
        </div>
      )}

      <div className="ai-actions">
        {assignError && (
          <div className="ai-action-error">{assignError}</div>
        )}
        {briefError && (
          <div className="ai-action-error">{briefError}</div>
        )}

        {bestMatch && canAssign && (
          <RoleGate allow={["manager", "admin"]}>
            <button
              className="primary-button assign-now-button"
              onClick={handleAssignNow}
              disabled={assigning}
            >
              {assigning ? "Assigning..." : "Assign & Start Trip"}
            </button>
          </RoleGate>
        )}

        <button
          className="secondary-button search-brief-button"
          onClick={handleOpenBrief}
          disabled={briefLoading}
        >
          {briefLoading
            ? "Generating..."
            : "📋 External Search Brief"}
        </button>
      </div>

      {brief && (
        <SearchBriefModal
          brief={brief}
          onClose={() => setBrief(null)}
        />
      )}
    </div>
  );
}


export default AIRecommendation;
