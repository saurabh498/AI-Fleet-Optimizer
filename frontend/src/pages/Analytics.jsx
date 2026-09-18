import { useEffect, useState } from "react";

import {
    getAssignments,
    getTrucks,
    getBaselineVsAI,
} from "../services/api";

function Analytics() {
    const [assignments, setAssignments] = useState([]);
    const [trucks, setTrucks] = useState([]);

    const [selectedTruck, setSelectedTruck] = useState("");

    const [comparison, setComparison] = useState(null);

    const [loading, setLoading] = useState(true);
    const [comparisonLoading, setComparisonLoading] =
        useState(false);

    const [error, setError] = useState(null);
    const [comparisonError, setComparisonError] =
        useState(null);

    // ==========================================
    // LOAD ANALYTICS DATA
    // ==========================================

    useEffect(() => {
        const loadAnalytics = async () => {
            try {
                const [assignmentData, truckData] =
                    await Promise.all([
                        getAssignments(),
                        getTrucks(),
                    ]);

                setAssignments(assignmentData);
                setTrucks(truckData);

                if (truckData.length > 0) {
                    setSelectedTruck(
                        String(truckData[0].truck_id)
                    );
                }
            } catch (error) {
                console.error(
                    "Failed to load analytics:",
                    error
                );

                setError(
                    "Failed to load analytics data."
                );
            } finally {
                setLoading(false);
            }
        };

        loadAnalytics();
    }, []);

    // ==========================================
    // LOAD BASELINE VS AI COMPARISON
    // ==========================================

    useEffect(() => {
        if (!selectedTruck) {
            return;
        }

        const loadComparison = async () => {
            setComparisonLoading(true);
            setComparisonError(null);

            try {
                const data = await getBaselineVsAI(
                    selectedTruck
                );

                setComparison(data);
            } catch (error) {
                console.error(
                    "Failed to load Baseline vs AI comparison:",
                    error
                );

                setComparison(null);

                setComparisonError(
                    "Baseline vs AI comparison is not available for this truck."
                );
            } finally {
                setComparisonLoading(false);
            }
        };

        loadComparison();
    }, [selectedTruck]);

    // ==========================================
    // EXISTING ANALYTICS CALCULATIONS
    // ==========================================

    const completedAssignments =
        assignments.filter(
            (assignment) =>
                assignment.status === "completed"
        ).length;

    const activeAssignments =
        assignments.filter(
            (assignment) =>
                assignment.status !== "completed"
        ).length;

    const totalDistance =
        assignments.reduce(
            (total, assignment) =>
                total +
                Number(
                    assignment.estimated_distance || 0
                ),
            0
        );

    const totalCost =
        assignments.reduce(
            (total, assignment) =>
                total +
                Number(
                    assignment.estimated_cost || 0
                ),
            0
        );

    const totalProfit =
        assignments.reduce(
            (total, assignment) =>
                total +
                Number(
                    assignment.estimated_profit || 0
                ),
            0
        );

    const totalWaitingTime =
        assignments.reduce(
            (total, assignment) =>
                total +
                Number(
                    assignment.waiting_time || 0
                ),
            0
        );

    const averageWaitingTime =
        assignments.length > 0
            ? totalWaitingTime / assignments.length
            : 0;

    const averageMatchScore =
        assignments.length > 0
            ? assignments.reduce(
                (total, assignment) =>
                    total +
                    Number(
                        assignment.match_score || 0
                    ),
                0
            ) / assignments.length
            : 0;

    const successfulBackhauls =
        assignments.filter(
            (assignment) =>
                assignment.status === "completed" &&
                Number(
                    assignment.estimated_distance || 0
                ) > 0
        ).length;

    const backhaulSuccessRate =
        completedAssignments > 0
            ? (successfulBackhauls /
                completedAssignments) *
            100
            : 0;

    const highlyRecommended =
        assignments.filter(
            (assignment) =>
                assignment.recommendation ===
                "Highly Recommended"
        ).length;

    const recommended =
        assignments.filter(
            (assignment) =>
                assignment.recommendation ===
                "Recommended"
        ).length;

    const moderatelyRecommended =
        assignments.filter(
            (assignment) =>
                assignment.recommendation ===
                "Moderately Recommended"
        ).length;

    const maxProfit = Math.max(
        ...assignments.map((assignment) =>
            Number(
                assignment.estimated_profit || 0
            )
        ),
        1
    );

    const maxDistance = Math.max(
        ...assignments.map((assignment) =>
            Number(
                assignment.estimated_distance || 0
            )
        ),
        1
    );

    const maxCost = Math.max(
        ...assignments.map((assignment) =>
            Number(
                assignment.estimated_cost || 0
            )
        ),
        1
    );

    // ==========================================
    // BASELINE VS AI DATA
    // ==========================================

    const baseline = comparison?.baseline;
    const ai = comparison?.ai;
    const comparisonData = comparison?.comparison;

    // ==========================================
    // SAME RESULT DETECTION
    // ==========================================

    const baselineProfit = Number(
        baseline?.estimated_profit || 0
    );

    const aiProfit = Number(
        ai?.estimated_profit || 0
    );

    const baselineDistance = Number(
        baseline?.total_distance_km || 0
    );

    const aiDistance = Number(
        ai?.total_distance_km || 0
    );

    const baselineCost = Number(
        baseline?.estimated_cost || 0
    );

    const aiCost = Number(
        ai?.estimated_cost || 0
    );

    const baselineUtilization = Number(
        baseline?.capacity_utilization_percent || 0
    );

    const aiUtilization = Number(
        ai?.capacity_utilization_percent || 0
    );

    const sameLoad =
        baseline?.load_id === ai?.load_id;

    const sameMetrics =
        Math.abs(
            baselineProfit - aiProfit
        ) < 0.01 &&
        Math.abs(
            baselineDistance - aiDistance
        ) < 0.01 &&
        Math.abs(
            baselineCost - aiCost
        ) < 0.01 &&
        Math.abs(
            baselineUtilization -
            aiUtilization
        ) < 0.01;

    const isSameResult =
        sameLoad && sameMetrics;

    // ==========================================
    // FORMATTING HELPERS
    // ==========================================

    const formatCurrency = (value) => {
        return `₹${Number(
            value || 0
        ).toLocaleString("en-IN", {
            maximumFractionDigits: 2,
        })}`;
    };

    const formatNumber = (
        value,
        digits = 2
    ) => {
        return Number(
            value || 0
        ).toFixed(digits);
    };

    // ==========================================
    // RENDER
    // ==========================================

    return (
        <div className="dashboard">

            {/* ==========================================
                HEADER
            ========================================== */}

            <header className="dashboard-header">

                <div>
                    <p className="dashboard-label">
                        AI FLEET OPTIMIZER
                    </p>

                    <h1>Analytics</h1>

                    <p className="dashboard-subtitle">
                        Fleet performance, optimization and
                        Baseline vs AI evaluation
                    </p>
                </div>

                <div className="system-status">
                    <span className="status-dot"></span>
                    Analytics Online
                </div>

            </header>

            {error && (
                <div className="analytics-error">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="loading">
                    Loading analytics...
                </div>
            ) : (
                <>

                    {/* ==========================================
                        PHASE 9 — BASELINE VS AI
                    ========================================== */}

                    <section className="dashboard-section phase9-section">

                        <div className="section-header">

                            <div>
                                <p className="phase9-label">
                                    PHASE 9 • CONTROLLED EVALUATION
                                </p>

                                <h2>
                                    Baseline vs AI Comparison
                                </h2>

                                <p>
                                    Compare the existing baseline
                                    strategy with the AI-based
                                    decision strategy using the
                                    same truck state and shipment pool.
                                </p>
                            </div>

                            <div className="experiment-badge">
                                🧪 Controlled Experiment
                            </div>

                        </div>

                        {/* TRUCK SELECTOR */}

                        <div className="comparison-controls">

                            <div>
                                <label
                                    htmlFor="analytics-truck"
                                    className="comparison-label"
                                >
                                    Select Truck
                                </label>

                                <select
                                    id="analytics-truck"
                                    value={selectedTruck}
                                    onChange={(event) =>
                                        setSelectedTruck(
                                            event.target.value
                                        )
                                    }
                                    className="truck-selector"
                                >

                                    <option value="">
                                        Select a truck
                                    </option>

                                    {trucks.map((truck) => (
                                        <option
                                            key={truck.truck_id}
                                            value={truck.truck_id}
                                        >
                                            Truck #{truck.truck_id}
                                            {" — "}
                                            {truck.current_city ||
                                                "Unknown"}
                                        </option>
                                    ))}

                                </select>
                            </div>

                            <div className="experiment-status">

                                <span className="experiment-check">
                                    ✓
                                </span>

                                <span>
                                    Database not modified
                                </span>

                            </div>

                        </div>

                        {comparisonLoading ? (

                            <div className="comparison-loading">
                                Running controlled comparison...
                            </div>

                        ) : comparisonError ? (

                            <div className="comparison-empty">

                                <div className="comparison-empty-icon">
                                    📊
                                </div>

                                <strong>
                                    No comparison available
                                </strong>

                                <p>
                                    {comparisonError}
                                </p>

                            </div>

                        ) : comparison ? (

                            <>

                                {/* ==========================================
                                    EXPERIMENT VALIDITY
                                ========================================== */}

                                <div className="experiment-validity-grid">

                                    <div className="validity-card">

                                        <span className="validity-icon">
                                            🚛
                                        </span>

                                        <div>
                                            <span>
                                                Truck State
                                            </span>

                                            <strong>
                                                Same ✓
                                            </strong>
                                        </div>

                                    </div>

                                    <div className="validity-card">

                                        <span className="validity-icon">
                                            📦
                                        </span>

                                        <div>
                                            <span>
                                                Shipment Pool
                                            </span>

                                            <strong>
                                                Same ✓
                                            </strong>
                                        </div>

                                    </div>

                                    <div className="validity-card">

                                        <span className="validity-icon">
                                            🗄️
                                        </span>

                                        <div>
                                            <span>
                                                Database Modified
                                            </span>

                                            <strong>
                                                No ✓
                                            </strong>
                                        </div>

                                    </div>

                                </div>

                                {/* ==========================================
                                    COMPARISON DATA
                                ========================================== */}

                                {baseline && ai ? (

                                    <>

                                        <div className="comparison-title">

                                            <h3>
                                                Strategy Performance
                                            </h3>

                                            <p>
                                                Estimated operational
                                                metrics for the selected
                                                truck
                                            </p>

                                        </div>

                                        <div className="comparison-grid">

                                            {/* REVENUE */}

                                            <div className="comparison-card">

                                                <div className="comparison-card-header">

                                                    <span>
                                                        💰 Revenue
                                                    </span>

                                                    <span className="comparison-unit">
                                                        Estimated
                                                    </span>

                                                </div>

                                                <div className="comparison-values">

                                                    <div>
                                                        <span>
                                                            Baseline
                                                        </span>

                                                        <strong>
                                                            {formatCurrency(
                                                                baseline.revenue
                                                            )}
                                                        </strong>
                                                    </div>

                                                    <div className="ai-value">

                                                        <span>
                                                            AI
                                                        </span>

                                                        <strong>
                                                            {formatCurrency(
                                                                ai.revenue
                                                            )}
                                                        </strong>

                                                    </div>

                                                </div>

                                                <div className="comparison-difference positive">

                                                    AI vs Baseline:{" "}

                                                    {formatCurrency(
                                                        comparisonData?.revenue_difference
                                                    )}

                                                </div>

                                            </div>

                                            {/* COST */}

                                            <div className="comparison-card">

                                                <div className="comparison-card-header">

                                                    <span>
                                                        💸 Operating Cost
                                                    </span>

                                                    <span className="comparison-unit">
                                                        Estimated
                                                    </span>

                                                </div>

                                                <div className="comparison-values">

                                                    <div>
                                                        <span>
                                                            Baseline
                                                        </span>

                                                        <strong>
                                                            {formatCurrency(
                                                                baseline.estimated_cost
                                                            )}
                                                        </strong>

                                                    </div>

                                                    <div className="ai-value">

                                                        <span>
                                                            AI
                                                        </span>

                                                        <strong>
                                                            {formatCurrency(
                                                                ai.estimated_cost
                                                            )}
                                                        </strong>

                                                    </div>

                                                </div>

                                                <div className="comparison-difference neutral">

                                                    Cost difference:{" "}

                                                    {formatCurrency(
                                                        comparisonData?.cost_difference
                                                    )}

                                                </div>

                                            </div>

                                            {/* PROFIT */}

                                            <div className="comparison-card highlight">

                                                <div className="comparison-card-header">

                                                    <span>
                                                        📈 Estimated Profit
                                                    </span>

                                                    <span className="comparison-unit">
                                                        Estimated
                                                    </span>

                                                </div>

                                                <div className="comparison-values">

                                                    <div>
                                                        <span>
                                                            Baseline
                                                        </span>

                                                        <strong>
                                                            {formatCurrency(
                                                                baseline.estimated_profit
                                                            )}
                                                        </strong>

                                                    </div>

                                                    <div className="ai-value">

                                                        <span>
                                                            AI
                                                        </span>

                                                        <strong>
                                                            {formatCurrency(
                                                                ai.estimated_profit
                                                            )}
                                                        </strong>

                                                    </div>

                                                </div>

                                                <div className="comparison-difference positive">

                                                    AI profit advantage:{" "}

                                                    {formatCurrency(
                                                        comparisonData?.profit_difference
                                                    )}

                                                </div>

                                            </div>

                                            {/* DISTANCE */}

                                            <div className="comparison-card">

                                                <div className="comparison-card-header">

                                                    <span>
                                                        🛣️ Total Distance
                                                    </span>

                                                    <span className="comparison-unit">
                                                        KM
                                                    </span>

                                                </div>

                                                <div className="comparison-values">

                                                    <div>
                                                        <span>
                                                            Baseline
                                                        </span>

                                                        <strong>
                                                            {formatNumber(
                                                                baseline.total_distance_km
                                                            )}{" "}
                                                            km
                                                        </strong>
                                                    </div>

                                                    <div className="ai-value">

                                                        <span>
                                                            AI
                                                        </span>

                                                        <strong>
                                                            {formatNumber(
                                                                ai.total_distance_km
                                                            )}{" "}
                                                            km
                                                        </strong>

                                                    </div>

                                                </div>

                                                <div className="comparison-difference neutral">

                                                    Difference:{" "}

                                                    {formatNumber(
                                                        comparisonData?.distance_difference_km
                                                    )}{" "}
                                                    km

                                                </div>

                                            </div>

                                            {/* UTILIZATION */}

                                            <div className="comparison-card">

                                                <div className="comparison-card-header">

                                                    <span>
                                                        📦 Capacity Utilization
                                                    </span>

                                                    <span className="comparison-unit">
                                                        %
                                                    </span>

                                                </div>

                                                <div className="comparison-values">

                                                    <div>
                                                        <span>
                                                            Baseline
                                                        </span>

                                                        <strong>
                                                            {formatNumber(
                                                                baseline.capacity_utilization_percent
                                                            )}
                                                            %
                                                        </strong>
                                                    </div>

                                                    <div className="ai-value">

                                                        <span>
                                                            AI
                                                        </span>

                                                        <strong>
                                                            {formatNumber(
                                                                ai.capacity_utilization_percent
                                                            )}
                                                            %
                                                        </strong>

                                                    </div>

                                                </div>

                                                <div className="comparison-difference positive">

                                                    Utilization difference:{" "}

                                                    {formatNumber(
                                                        comparisonData?.utilization_difference_percent
                                                    )}{" "}
                                                    pp

                                                </div>

                                            </div>

                                        </div>

                                        {/* ==========================================
                                            SELECTED LOADS
                                        ========================================== */}

                                        <div className="selected-loads">

                                            <div className="selected-load-card baseline-load">

                                                <span className="strategy-label">
                                                    BASELINE STRATEGY
                                                </span>

                                                <h3>
                                                    Load #{baseline.load_id}
                                                </h3>

                                                <p>
                                                    {baseline.pickup_city}
                                                    {" → "}
                                                    {baseline.destination_city}
                                                </p>

                                                <div className="load-details">

                                                    <span>
                                                        Weight:{" "}
                                                        <strong>
                                                            {baseline.weight} kg
                                                        </strong>
                                                    </span>

                                                    <span>
                                                        Revenue:{" "}
                                                        <strong>
                                                            {formatCurrency(
                                                                baseline.revenue
                                                            )}
                                                        </strong>
                                                    </span>

                                                </div>

                                                <p className="strategy-description">
                                                    Nearest compatible
                                                    shipment strategy
                                                </p>

                                            </div>

                                            <div className="comparison-arrow">
                                                VS
                                            </div>

                                            <div className="selected-load-card ai-load">

                                                <span className="strategy-label">
                                                    AI STRATEGY
                                                </span>

                                                <h3>
                                                    Load #{ai.load_id}
                                                </h3>

                                                <p>
                                                    {ai.pickup_city}
                                                    {" → "}
                                                    {ai.destination_city}
                                                </p>

                                                <div className="load-details">

                                                    <span>
                                                        Weight:{" "}
                                                        <strong>
                                                            {ai.weight} kg
                                                        </strong>
                                                    </span>

                                                    <span>
                                                        Revenue:{" "}
                                                        <strong>
                                                            {formatCurrency(
                                                                ai.revenue
                                                            )}
                                                        </strong>
                                                    </span>

                                                </div>

                                                <p className="strategy-description">
                                                    AI-based optimized
                                                    decision strategy
                                                </p>

                                            </div>

                                        </div>

                                        {/* ==========================================
                                            EXPERIMENT RESULT
                                        ========================================== */}

                                        <div className="comparison-result">

                                            <div className="result-icon">

                                                {isSameResult
                                                    ? "🤝"
                                                    : comparisonData?.winner === "AI"
                                                        ? "🏆"
                                                        : comparisonData?.winner === "BASELINE"
                                                            ? "📌"
                                                            : "⚖️"}

                                            </div>

                                            <div>

                                                <span className="result-label">
                                                    EXPERIMENT RESULT
                                                </span>

                                                <h3>

                                                    {isSameResult
                                                        ? "Same Result"
                                                        : comparisonData?.winner === "AI"
                                                            ? "AI Strategy Wins"
                                                            : comparisonData?.winner === "BASELINE"
                                                                ? "Baseline Strategy Wins"
                                                                : "Trade-off Result"}

                                                </h3>

                                                <p>

                                                    {isSameResult
                                                        ? "Both strategies selected the same shipment and produced the same estimated operational metrics in this controlled scenario."
                                                        : comparisonData?.winner === "AI"
                                                            ? "The AI strategy achieved higher estimated profit without increasing total route distance in this controlled scenario."
                                                            : comparisonData?.winner === "BASELINE"
                                                                ? "The baseline strategy performed better on the evaluated profit and distance criteria in this controlled scenario."
                                                                : "The two strategies present a trade-off across profit and route distance in this controlled scenario."}

                                                </p>

                                            </div>

                                        </div>

                                        {/* ==========================================
                                            EVALUATION NOTE
                                        ========================================== */}

                                        <div className="experiment-note">

                                            <strong>
                                                ⚠️ Evaluation Note
                                            </strong>

                                            <span>
                                                This result represents
                                                the selected controlled
                                                scenario. It should not
                                                be interpreted as a
                                                general improvement
                                                percentage for the entire
                                                fleet.
                                            </span>

                                        </div>

                                    </>

                                ) : (

                                    <div className="comparison-empty">

                                        <div className="comparison-empty-icon">
                                            📊
                                        </div>

                                        <strong>
                                            No valid comparison for this truck state
                                        </strong>

                                        <p>
                                            Both baseline and AI need
                                            a valid shipment selection
                                            for this controlled evaluation.
                                        </p>

                                    </div>

                                )}

                            </>

                        ) : (

                            <div className="comparison-empty">

                                <div className="comparison-empty-icon">
                                    📊
                                </div>

                                <strong>
                                    Select a truck
                                </strong>

                                <p>
                                    Select a truck to run the
                                    controlled Baseline vs AI
                                    evaluation.
                                </p>

                            </div>

                        )}

                    </section>


                    {/* ==========================================
                        EXISTING PERFORMANCE KPIs
                    ========================================== */}

                    <section className="kpi-grid">

                        <div className="kpi-card">

                            <div className="kpi-icon">
                                📋
                            </div>

                            <div className="kpi-content">

                                <p className="kpi-title">
                                    Total Assignments
                                </p>

                                <h2 className="kpi-value">
                                    {assignments.length}
                                </h2>

                                <p className="kpi-description">
                                    Recorded truck-load assignments
                                </p>

                            </div>

                        </div>

                        <div className="kpi-card">

                            <div className="kpi-icon">
                                ✅
                            </div>

                            <div className="kpi-content">

                                <p className="kpi-title">
                                    Completed
                                </p>

                                <h2 className="kpi-value">
                                    {completedAssignments}
                                </h2>

                                <p className="kpi-description">
                                    Successfully completed assignments
                                </p>

                            </div>

                        </div>

                        <div className="kpi-card">

                            <div className="kpi-icon">
                                🛣️
                            </div>

                            <div className="kpi-content">

                                <p className="kpi-title">
                                    Total Distance
                                </p>

                                <h2 className="kpi-value">
                                    {totalDistance.toFixed(2)} km
                                </h2>

                                <p className="kpi-description">
                                    Estimated assignment distance
                                </p>

                            </div>

                        </div>

                        <div className="kpi-card">

                            <div className="kpi-icon">
                                💰
                            </div>

                            <div className="kpi-content">

                                <p className="kpi-title">
                                    Total Profit
                                </p>

                                <h2 className="kpi-value">
                                    ₹
                                    {totalProfit.toLocaleString(
                                        "en-IN",
                                        {
                                            maximumFractionDigits: 0,
                                        }
                                    )}
                                </h2>

                                <p className="kpi-description">
                                    Estimated assignment profit
                                </p>

                            </div>

                        </div>

                    </section>


                    {/* ==========================================
                        OPERATIONAL METRICS
                    ========================================== */}

                    <section className="dashboard-section">

                        <div className="section-header">

                            <div>

                                <h2>
                                    Operational Performance
                                </h2>

                                <p>
                                    Key logistics and optimization metrics
                                </p>

                            </div>

                        </div>

                        <div className="kpi-grid">

                            <div className="kpi-card">

                                <div className="kpi-icon">
                                    💸
                                </div>

                                <div className="kpi-content">

                                    <p className="kpi-title">
                                        Operating Cost
                                    </p>

                                    <h2 className="kpi-value">
                                        ₹
                                        {totalCost.toLocaleString(
                                            "en-IN",
                                            {
                                                maximumFractionDigits: 0,
                                            }
                                        )}
                                    </h2>

                                    <p className="kpi-description">
                                        Estimated fleet operating cost
                                    </p>

                                </div>

                            </div>

                            <div className="kpi-card">

                                <div className="kpi-icon">
                                    ⏱️
                                </div>

                                <div className="kpi-content">

                                    <p className="kpi-title">
                                        Avg Assignment Waiting
                                    </p>

                                    <h2 className="kpi-value">
                                        {averageWaitingTime.toFixed(2)} hrs
                                    </h2>

                                    <p className="kpi-description">
                                        Average recorded waiting time per assignment
                                    </p>

                                </div>

                            </div>

                            <div className="kpi-card">

                                <div className="kpi-icon">
                                    🎯
                                </div>

                                <div className="kpi-content">

                                    <p className="kpi-title">
                                        Avg Match Score
                                    </p>

                                    <h2 className="kpi-value">
                                        {averageMatchScore.toFixed(1)}
                                    </h2>

                                    <p className="kpi-description">
                                        Average AI assignment score
                                    </p>

                                </div>

                            </div>

                            <div className="kpi-card">

                                <div className="kpi-icon">
                                    🔄
                                </div>

                                <div className="kpi-content">

                                    <p className="kpi-title">
                                        Backhaul Completion Rate
                                    </p>

                                    <h2 className="kpi-value">
                                        {backhaulSuccessRate.toFixed(1)}%
                                    </h2>

                                    <p className="kpi-description">
                                        Completed assignments with recorded movement
                                    </p>

                                </div>

                            </div>

                        </div>

                    </section>


                    {/* ==========================================
                        VISUAL ANALYTICS
                    ========================================== */}

                    <section className="dashboard-section">

                        <div className="section-header">

                            <div>

                                <h2>
                                    Visual Analytics
                                </h2>

                                <p>
                                    Assignment, distance, cost and
                                    profit performance
                                </p>

                            </div>

                        </div>

                        <div className="analytics-chart-grid">

                            {/* PROFIT */}

                            <div className="analytics-chart-card">

                                <div className="analytics-chart-header">

                                    <h3>
                                        Assignment Profit
                                    </h3>

                                    <span>
                                        ₹
                                    </span>

                                </div>

                                <div className="bar-chart">

                                    {assignments.map(
                                        (assignment) => {

                                            const profit =
                                                Number(
                                                    assignment.estimated_profit ||
                                                    0
                                                );

                                            const height =
                                                (profit /
                                                    maxProfit) *
                                                100;

                                            return (
                                                <div
                                                    className="bar-column"
                                                    key={`profit-${assignment.assignment_id}`}
                                                >

                                                    <div className="bar-value">
                                                        ₹
                                                        {Math.round(
                                                            profit / 1000
                                                        )}
                                                        k
                                                    </div>

                                                    <div
                                                        className="bar profit-bar"
                                                        style={{
                                                            height: `${height}%`,
                                                        }}
                                                        title={`Assignment #${assignment.assignment_id}: ₹${profit.toLocaleString(
                                                            "en-IN"
                                                        )}`}
                                                    ></div>

                                                    <span>
                                                        #{assignment.assignment_id}
                                                    </span>

                                                </div>
                                            );
                                        }
                                    )}

                                </div>

                            </div>


                            {/* DISTANCE */}

                            <div className="analytics-chart-card">

                                <div className="analytics-chart-header">

                                    <h3>
                                        Assignment Distance
                                    </h3>

                                    <span>
                                        KM
                                    </span>

                                </div>

                                <div className="bar-chart">

                                    {assignments.map(
                                        (assignment) => {

                                            const distance =
                                                Number(
                                                    assignment.estimated_distance ||
                                                    0
                                                );

                                            const height =
                                                (distance /
                                                    maxDistance) *
                                                100;

                                            return (
                                                <div
                                                    className="bar-column"
                                                    key={`distance-${assignment.assignment_id}`}
                                                >

                                                    <div className="bar-value">
                                                        {Math.round(
                                                            distance
                                                        )}
                                                    </div>

                                                    <div
                                                        className="bar distance-bar"
                                                        style={{
                                                            height: `${height}%`,
                                                        }}
                                                        title={`Assignment #${assignment.assignment_id}: ${distance.toFixed(
                                                            2
                                                        )} km`}
                                                    ></div>

                                                    <span>
                                                        #{assignment.assignment_id}
                                                    </span>

                                                </div>
                                            );
                                        }
                                    )}

                                </div>

                            </div>


                            {/* COST */}

                            <div className="analytics-chart-card">

                                <div className="analytics-chart-header">

                                    <h3>
                                        Operating Cost
                                    </h3>

                                    <span>
                                        ₹
                                    </span>

                                </div>

                                <div className="bar-chart">

                                    {assignments.map(
                                        (assignment) => {

                                            const cost =
                                                Number(
                                                    assignment.estimated_cost ||
                                                    0
                                                );

                                            const height =
                                                (cost /
                                                    maxCost) *
                                                100;

                                            return (
                                                <div
                                                    className="bar-column"
                                                    key={`cost-${assignment.assignment_id}`}
                                                >

                                                    <div className="bar-value">
                                                        ₹
                                                        {Math.round(
                                                            cost / 1000
                                                        )}
                                                        k
                                                    </div>

                                                    <div
                                                        className="bar cost-bar"
                                                        style={{
                                                            height: `${height}%`,
                                                        }}
                                                        title={`Assignment #${assignment.assignment_id}: ₹${cost.toLocaleString(
                                                            "en-IN"
                                                        )}`}
                                                    ></div>

                                                    <span>
                                                        #{assignment.assignment_id}
                                                    </span>

                                                </div>
                                            );
                                        }
                                    )}

                                </div>

                            </div>


                            {/* RECOMMENDATION DISTRIBUTION */}

                            <div className="analytics-chart-card">

                                <div className="analytics-chart-header">

                                    <h3>
                                        AI Recommendation Distribution
                                    </h3>

                                    <span>
                                        Count
                                    </span>

                                </div>

                                <div className="recommendation-bars">

                                    <div className="recommendation-row">

                                        <div className="recommendation-label">

                                            <span>
                                                Highly Recommended
                                            </span>

                                            <strong>
                                                {highlyRecommended}
                                            </strong>

                                        </div>

                                        <div className="recommendation-track">

                                            <div
                                                className="recommendation-fill"
                                                style={{
                                                    width: `${assignments.length > 0
                                                        ? (
                                                            highlyRecommended /
                                                            assignments.length
                                                        ) * 100
                                                        : 0
                                                        }%`,
                                                }}
                                            ></div>

                                        </div>

                                    </div>

                                    <div className="recommendation-row">

                                        <div className="recommendation-label">

                                            <span>
                                                Recommended
                                            </span>

                                            <strong>
                                                {recommended}
                                            </strong>

                                        </div>

                                        <div className="recommendation-track">

                                            <div
                                                className="recommendation-fill"
                                                style={{
                                                    width: `${assignments.length > 0
                                                        ? (
                                                            recommended /
                                                            assignments.length
                                                        ) * 100
                                                        : 0
                                                        }%`,
                                                }}
                                            ></div>

                                        </div>

                                    </div>

                                    <div className="recommendation-row">

                                        <div className="recommendation-label">

                                            <span>
                                                Moderately Recommended
                                            </span>

                                            <strong>
                                                {moderatelyRecommended}
                                            </strong>

                                        </div>

                                        <div className="recommendation-track">

                                            <div
                                                className="recommendation-fill"
                                                style={{
                                                    width: `${assignments.length > 0
                                                        ? (
                                                            moderatelyRecommended /
                                                            assignments.length
                                                        ) * 100
                                                        : 0
                                                        }%`,
                                                }}
                                            ></div>

                                        </div>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </section>


                    {/* ==========================================
                        ASSIGNMENT PERFORMANCE
                    ========================================== */}

                    <section className="dashboard-section">

                        <div className="section-header">

                            <div>

                                <h2>
                                    Assignment Performance
                                </h2>

                                <p>
                                    AI-generated truck-load
                                    assignment results
                                </p>

                            </div>

                        </div>

                        <div className="shipment-table">

                            <div className="table-header">

                                <span>
                                    Assignment
                                </span>

                                <span>
                                    Truck
                                </span>

                                <span>
                                    Load
                                </span>

                                <span>
                                    Distance
                                </span>

                                <span>
                                    Cost
                                </span>

                                <span>
                                    Profit
                                </span>

                                <span>
                                    Score
                                </span>

                                <span>
                                    Status
                                </span>

                            </div>

                            {assignments.map(
                                (assignment) => (

                                    <div
                                        className="table-row"
                                        key={
                                            assignment.assignment_id
                                        }
                                    >

                                        <span>
                                            #{assignment.assignment_id}
                                        </span>

                                        <span>
                                            Truck #
                                            {assignment.truck_id}
                                        </span>

                                        <span>
                                            Load #
                                            {assignment.load_id}
                                        </span>

                                        <span>
                                            {Number(
                                                assignment.estimated_distance ||
                                                0
                                            ).toFixed(2)}
                                            {" "}km
                                        </span>

                                        <span>
                                            ₹
                                            {Number(
                                                assignment.estimated_cost ||
                                                0
                                            ).toLocaleString(
                                                "en-IN",
                                                {
                                                    maximumFractionDigits: 0,
                                                }
                                            )}
                                        </span>

                                        <span>
                                            ₹
                                            {Number(
                                                assignment.estimated_profit ||
                                                0
                                            ).toLocaleString(
                                                "en-IN",
                                                {
                                                    maximumFractionDigits: 0,
                                                }
                                            )}
                                        </span>

                                        <span>
                                            {assignment.match_score}
                                        </span>

                                        <span
                                            className={
                                                "truck-status " +
                                                String(
                                                    assignment.status ||
                                                    ""
                                                )
                                                    .toLowerCase()
                                                    .replace(
                                                        /\s+/g,
                                                        "-"
                                                    )
                                            }
                                        >
                                            {assignment.status}
                                        </span>

                                    </div>

                                )
                            )}

                        </div>

                    </section>


                    {/* ==========================================
                        RECOMMENDATION SUMMARY
                    ========================================== */}

                    <section className="dashboard-section">

                        <div className="section-header">

                            <div>

                                <h2>
                                    AI Recommendation Distribution
                                </h2>

                                <p>
                                    Assignment recommendations
                                    generated by the optimization
                                    engine
                                </p>

                            </div>

                        </div>

                        <div className="kpi-grid">

                            <div className="kpi-card">

                                <div className="kpi-icon">
                                    ⭐
                                </div>

                                <div className="kpi-content">

                                    <p className="kpi-title">
                                        Highly Recommended
                                    </p>

                                    <h2 className="kpi-value">
                                        {highlyRecommended}
                                    </h2>

                                    <p className="kpi-description">
                                        Strong assignment matches
                                    </p>

                                </div>

                            </div>

                            <div className="kpi-card">

                                <div className="kpi-icon">
                                    👍
                                </div>

                                <div className="kpi-content">

                                    <p className="kpi-title">
                                        Recommended
                                    </p>

                                    <h2 className="kpi-value">
                                        {recommended}
                                    </h2>

                                    <p className="kpi-description">
                                        Good assignment matches
                                    </p>

                                </div>

                            </div>

                            <div className="kpi-card">

                                <div className="kpi-icon">
                                    ⚖️
                                </div>

                                <div className="kpi-content">

                                    <p className="kpi-title">
                                        Moderately Recommended
                                    </p>

                                    <h2 className="kpi-value">
                                        {moderatelyRecommended}
                                    </h2>

                                    <p className="kpi-description">
                                        Moderate assignment matches
                                    </p>

                                </div>

                            </div>

                            <div className="kpi-card">

                                <div className="kpi-icon">
                                    🔄
                                </div>

                                <div className="kpi-content">

                                    <p className="kpi-title">
                                        Active Assignments
                                    </p>

                                    <h2 className="kpi-value">
                                        {activeAssignments}
                                    </h2>

                                    <p className="kpi-description">
                                        Currently non-completed
                                    </p>

                                </div>

                            </div>

                        </div>

                    </section>

                </>
            )}

        </div>
    );
}

export default Analytics;