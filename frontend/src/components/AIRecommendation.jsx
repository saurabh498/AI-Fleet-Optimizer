function AIRecommendation({ recommendation }) {
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

  return (
    <div className="ai-recommendation-card">

      {/* Header */}

      <div className="ai-card-header">
        <div>
          <p className="ai-label">AI DECISION ENGINE</p>
          <h2>Truck #{recommendation.truck_id}</h2>
        </div>
        <span className={`decision-badge ${decisionClass}`}>
          {decision.replaceAll("_", " ")}
        </span>
      </div>

      {/* Main Decision */}

      <div className="ai-decision">
        <div className="ai-decision-icon">🤖</div>
        <div>
          <h3>{decision.replaceAll("_", " ")}</h3>
          <p>{recommendation.action}</p>
        </div>
      </div>

      {/* Reason */}

      <div className="ai-reason">
        <strong>AI Reason</strong>
        <p>{recommendation.reason}</p>
      </div>

      {/* Best Match */}

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

      {/* Decision Metrics */}

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
                  ? `+${metrics.ml_adjustment}`
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

      {/* Cost Breakdown */}

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

      {/* Environmental Impact */}

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

      {/* ML Context */}

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

      {/* ML Explanation */}

      {mlExplanation && (
        <div
          className={`ml-explanation ${(mlExplanation.impact || "NEUTRAL").toLowerCase()}`}
        >
          <strong>ML Impact: {mlExplanation.impact}</strong>
          <p>{mlExplanation.reason}</p>
        </div>
      )}

      {/* SHAP Explainability */}

      {shap?.summary && (
        <div className="shap-explanation">
          <div className="subsection-title">SHAP Explainability</div>

          <p className="shap-summary">{shap.summary}</p>

          {(shap.predicted_value != null || shap.base_value != null) && (
            <div className="shap-baseline">
              <span>Baseline: {Number(shap.base_value || 0).toFixed(2)}</span>
              <span>Prediction: {Number(shap.predicted_value || 0).toFixed(2)}</span>
            </div>
          )}

          {shap.top_drivers?.length > 0 && (
            <div className="shap-drivers">
              <strong className="shap-drivers-title">Pushing prediction up</strong>
              {shap.top_drivers.map((d, i) => (
                <div key={`pos-${i}`} className="shap-driver positive">
                  <span className="shap-feature">{d.feature}</span>
                  <span className="shap-value">{Number(d.value).toFixed(2)}</span>
                  <span className="shap-impact">
                    +{Number(d.impact).toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          )}

          {shap.top_negative?.length > 0 && (
            <div className="shap-drivers">
              <strong className="shap-drivers-title">Pulling prediction down</strong>
              {shap.top_negative.map((d, i) => (
                <div key={`neg-${i}`} className="shap-driver negative">
                  <span className="shap-feature">{d.feature}</span>
                  <span className="shap-value">{Number(d.value).toFixed(2)}</span>
                  <span className="shap-impact">
                    {Number(d.impact).toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

    </div>
  );
}

export default AIRecommendation;
