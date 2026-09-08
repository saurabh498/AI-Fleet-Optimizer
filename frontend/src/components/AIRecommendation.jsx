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

  return (
    <div className="ai-recommendation-card">

      {/* Header */}

      <div className="ai-card-header">

        <div>
          <p className="ai-label">
            AI DECISION ENGINE
          </p>

          <h2>
            Truck #{recommendation.truck_id}
          </h2>
        </div>

        <span className={`decision-badge ${decisionClass}`}>
          {decision.replaceAll("_", " ")}
        </span>

      </div>

      {/* Main Decision */}

      <div className="ai-decision">

        <div className="ai-decision-icon">
          🤖
        </div>

        <div>

          <h3>
            {decision.replaceAll("_", " ")}
          </h3>

          <p>
            {recommendation.action}
          </p>

        </div>

      </div>

      {/* Reason */}

      <div className="ai-reason">

        <strong>AI Reason</strong>

        <p>
          {recommendation.reason}
        </p>

      </div>

      {/* Best Match */}

      {bestMatch && (
        <div className="best-match">

          <div className="subsection-title">
            Best Backhaul Match
          </div>

          <div className="match-grid">

            <div>
              <span>Load</span>
              <strong>
                #{bestMatch.load_id}
              </strong>
            </div>

            <div>
              <span>Route</span>
              <strong>
                {bestMatch.pickup_city} →{" "}
                {bestMatch.destination_city}
              </strong>
            </div>

            <div>
              <span>Weight</span>
              <strong>
                {bestMatch.weight} kg
              </strong>
            </div>

            <div>
              <span>Revenue</span>
              <strong>
                ₹
                {Number(
                  bestMatch.revenue || 0
                ).toLocaleString("en-IN")}
              </strong>
            </div>

          </div>

        </div>
      )}

      {/* Decision Metrics */}

      {metrics && (
        <div className="ai-metrics">

          <div className="subsection-title">
            Decision Metrics
          </div>

          <div className="metrics-grid">

            <div className="metric">
              <span>Decision Score</span>
              <strong>
                {metrics.decision_score}
              </strong>
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
              <strong>
                {metrics.route_efficiency_score}%
              </strong>
            </div>

            <div className="metric">
              <span>Estimated Profit</span>
              <strong>
                ₹
                {Number(
                  metrics.estimated_route_profit || 0
                ).toLocaleString("en-IN")}
              </strong>
            </div>

          </div>

        </div>
      )}

      {/* ML Context */}

      {mlContext?.available && (
        <div className="ml-context">

          <div className="subsection-title">
            ML Prediction
          </div>

          <div className="metrics-grid">

            <div className="metric">
              <span>Predicted Demand</span>
              <strong>
                {mlContext.predicted_demand}
              </strong>
            </div>

            <div className="metric">
              <span>Predicted Waiting</span>
              <strong>
                {mlContext.predicted_waiting_time} hrs
              </strong>
            </div>

            <div className="metric">
              <span>Demand Model</span>
              <strong>
                {mlContext.demand_model}
              </strong>
            </div>

            <div className="metric">
              <span>Waiting Model</span>
              <strong>
                {mlContext.waiting_model}
              </strong>
            </div>

          </div>

        </div>
      )}

      {/* ML Explanation */}

      {mlExplanation && (
        <div className={`ml-explanation ${(
          mlExplanation.impact || "NEUTRAL"
        ).toLowerCase()}`}>

          <strong>
            ML Impact: {mlExplanation.impact}
          </strong>

          <p>
            {mlExplanation.reason}
          </p>

        </div>
      )}

    </div>
  );
}

export default AIRecommendation;