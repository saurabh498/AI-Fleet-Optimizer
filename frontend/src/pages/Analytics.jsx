import { useEffect, useState } from "react";

import { getAssignments } from "../services/api";

function Analytics() {
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadAnalytics = async () => {
            try {
                const data = await getAssignments();
                setAssignments(data);
            } catch (error) {
                console.error(
                    "Failed to load assignment analytics:",
                    error
                );
            } finally {
                setLoading(false);
            }
        };

        loadAnalytics();
    }, []);

    const completedAssignments = assignments.filter(
        (assignment) =>
            assignment.status === "completed"
    ).length;

    const activeAssignments = assignments.filter(
        (assignment) =>
            assignment.status !== "completed"
    ).length;

    const totalDistance = assignments.reduce(
        (total, assignment) =>
            total +
            Number(assignment.estimated_distance || 0),
        0
    );

    const totalCost = assignments.reduce(
        (total, assignment) =>
            total +
            Number(assignment.estimated_cost || 0),
        0
    );

    const totalProfit = assignments.reduce(
        (total, assignment) =>
            total +
            Number(assignment.estimated_profit || 0),
        0
    );

    const totalWaitingTime = assignments.reduce(
        (total, assignment) =>
            total +
            Number(assignment.waiting_time || 0),
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
                    Number(assignment.match_score || 0),
                0
            ) / assignments.length
            : 0;

    const successfulBackhauls =
        assignments.filter(
            (assignment) =>
                assignment.status === "completed" &&
                Number(assignment.estimated_distance || 0) > 0
        ).length;

    const backhaulSuccessRate =
        completedAssignments > 0
            ? (successfulBackhauls /
                completedAssignments) *
            100
            : 0;

    const highlyRecommended = assignments.filter(
        (assignment) =>
            assignment.recommendation === "Highly Recommended"
    ).length;

    const recommended = assignments.filter(
        (assignment) =>
            assignment.recommendation === "Recommended"
    ).length;

    const moderatelyRecommended = assignments.filter(
        (assignment) =>
            assignment.recommendation === "Moderately Recommended"
    ).length;

    const maxProfit = Math.max(
        ...assignments.map((assignment) =>
            Number(assignment.estimated_profit || 0)
        ),
        1
    );

    const maxDistance = Math.max(
        ...assignments.map((assignment) =>
            Number(assignment.estimated_distance || 0)
        ),
        1
    );

    const maxCost = Math.max(
        ...assignments.map((assignment) =>
            Number(assignment.estimated_cost || 0)
        ),
        1
    );

    return (
        <div className="dashboard">

            <header className="dashboard-header">

                <div>
                    <p className="dashboard-label">
                        AI FLEET OPTIMIZER
                    </p>

                    <h1>Analytics</h1>

                    <p className="dashboard-subtitle">
                        Fleet performance and assignment analytics
                    </p>
                </div>

                <div className="system-status">
                    <span className="status-dot"></span>
                    Analytics Online
                </div>

            </header>

            {loading ? (
                <div className="loading">
                    Loading analytics...
                </div>
            ) : (
                <>
                    {/* PERFORMANCE KPIs */}

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

                    {/* OPERATIONAL METRICS */}

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
                                        Avg Waiting
                                    </p>

                                    <h2 className="kpi-value">
                                        {averageWaitingTime.toFixed(2)} hrs
                                    </h2>

                                    <p className="kpi-description">
                                        Average assignment waiting time
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
                                        Backhaul Success
                                    </p>

                                    <h2 className="kpi-value">
                                        {backhaulSuccessRate.toFixed(1)}%
                                    </h2>

                                    <p className="kpi-description">
                                        Completed assignments with movement
                                    </p>
                                </div>
                            </div>

                        </div>

                    </section>

                    {/* VISUAL ANALYTICS */}

                    <section className="dashboard-section">

                        <div className="section-header">
                            <div>
                                <h2>Visual Analytics</h2>

                                <p>
                                    Assignment, distance, cost and profit performance
                                </p>
                            </div>
                        </div>

                        <div className="analytics-chart-grid">

                            {/* PROFIT CHART */}

                            <div className="analytics-chart-card">

                                <div className="analytics-chart-header">
                                    <h3>Assignment Profit</h3>
                                    <span>₹</span>
                                </div>

                                <div className="bar-chart">

                                    {assignments.map((assignment) => {
                                        const profit =
                                            Number(
                                                assignment.estimated_profit || 0
                                            );

                                        const height =
                                            (profit / maxProfit) * 100;

                                        return (
                                            <div
                                                className="bar-column"
                                                key={`profit-${assignment.assignment_id}`}
                                            >

                                                <div className="bar-value">
                                                    ₹{Math.round(profit / 1000)}k
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
                                    })}

                                </div>

                            </div>


                            {/* DISTANCE CHART */}

                            <div className="analytics-chart-card">

                                <div className="analytics-chart-header">
                                    <h3>Assignment Distance</h3>
                                    <span>KM</span>
                                </div>

                                <div className="bar-chart">

                                    {assignments.map((assignment) => {
                                        const distance =
                                            Number(
                                                assignment.estimated_distance || 0
                                            );

                                        const height =
                                            (distance / maxDistance) * 100;

                                        return (
                                            <div
                                                className="bar-column"
                                                key={`distance-${assignment.assignment_id}`}
                                            >

                                                <div className="bar-value">
                                                    {Math.round(distance)}
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
                                    })}

                                </div>

                            </div>


                            {/* COST CHART */}

                            <div className="analytics-chart-card">

                                <div className="analytics-chart-header">
                                    <h3>Operating Cost</h3>
                                    <span>₹</span>
                                </div>

                                <div className="bar-chart">

                                    {assignments.map((assignment) => {
                                        const cost =
                                            Number(
                                                assignment.estimated_cost || 0
                                            );

                                        const height =
                                            (cost / maxCost) * 100;

                                        return (
                                            <div
                                                className="bar-column"
                                                key={`cost-${assignment.assignment_id}`}
                                            >

                                                <div className="bar-value">
                                                    ₹{Math.round(cost / 1000)}k
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
                                    })}

                                </div>

                            </div>


                            {/* RECOMMENDATION DISTRIBUTION */}

                            <div className="analytics-chart-card">

                                <div className="analytics-chart-header">
                                    <h3>AI Recommendation Distribution</h3>
                                    <span>Count</span>
                                </div>

                                <div className="recommendation-bars">

                                    <div className="recommendation-row">

                                        <div className="recommendation-label">
                                            <span>Highly Recommended</span>
                                            <strong>{highlyRecommended}</strong>
                                        </div>

                                        <div className="recommendation-track">
                                            <div
                                                className="recommendation-fill"
                                                style={{
                                                    width: `${assignments.length > 0
                                                            ? (highlyRecommended /
                                                                assignments.length) *
                                                            100
                                                            : 0
                                                        }%`,
                                                }}
                                            ></div>
                                        </div>

                                    </div>


                                    <div className="recommendation-row">

                                        <div className="recommendation-label">
                                            <span>Recommended</span>
                                            <strong>{recommended}</strong>
                                        </div>

                                        <div className="recommendation-track">
                                            <div
                                                className="recommendation-fill"
                                                style={{
                                                    width: `${assignments.length > 0
                                                            ? (recommended /
                                                                assignments.length) *
                                                            100
                                                            : 0
                                                        }%`,
                                                }}
                                            ></div>
                                        </div>

                                    </div>


                                    <div className="recommendation-row">

                                        <div className="recommendation-label">
                                            <span>Moderately Recommended</span>
                                            <strong>
                                                {moderatelyRecommended}
                                            </strong>
                                        </div>

                                        <div className="recommendation-track">
                                            <div
                                                className="recommendation-fill"
                                                style={{
                                                    width: `${assignments.length > 0
                                                            ? (moderatelyRecommended /
                                                                assignments.length) *
                                                            100
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

                    {/* ASSIGNMENT ANALYTICS TABLE */}

                    <section className="dashboard-section">

                        <div className="section-header">

                            <div>
                                <h2>
                                    Assignment Performance
                                </h2>

                                <p>
                                    AI-generated truck-load assignment results
                                </p>
                            </div>

                        </div>

                        <div className="shipment-table">

                            <div className="table-header">
                                <span>Assignment</span>
                                <span>Truck</span>
                                <span>Load</span>
                                <span>Distance</span>
                                <span>Cost</span>
                                <span>Profit</span>
                                <span>Score</span>
                                <span>Status</span>
                            </div>

                            {assignments.map((assignment) => (
                                <div
                                    className="table-row"
                                    key={assignment.assignment_id}
                                >

                                    <span>
                                        #{assignment.assignment_id}
                                    </span>

                                    <span>
                                        Truck #{assignment.truck_id}
                                    </span>

                                    <span>
                                        Load #{assignment.load_id}
                                    </span>

                                    <span>
                                        {Number(
                                            assignment.estimated_distance || 0
                                        ).toFixed(2)} km
                                    </span>

                                    <span>
                                        ₹
                                        {Number(
                                            assignment.estimated_cost || 0
                                        ).toLocaleString("en-IN", {
                                            maximumFractionDigits: 0,
                                        })}
                                    </span>

                                    <span>
                                        ₹
                                        {Number(
                                            assignment.estimated_profit || 0
                                        ).toLocaleString("en-IN", {
                                            maximumFractionDigits: 0,
                                        })}
                                    </span>

                                    <span>
                                        {assignment.match_score}
                                    </span>

                                    <span
                                        className={
                                            "truck-status " +
                                            String(
                                                assignment.status || ""
                                            )
                                                .toLowerCase()
                                                .replace(/\s+/g, "-")
                                        }
                                    >
                                        {assignment.status}
                                    </span>

                                </div>
                            ))}

                        </div>

                    </section>

                    {/* RECOMMENDATION SUMMARY */}

                    <section className="dashboard-section">

                        <div className="section-header">

                            <div>
                                <h2>
                                    AI Recommendation Distribution
                                </h2>

                                <p>
                                    Assignment recommendations generated by the optimization engine
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
                                        {
                                            assignments.filter(
                                                (assignment) =>
                                                    assignment.recommendation ===
                                                    "Highly Recommended"
                                            ).length
                                        }
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
                                        {
                                            assignments.filter(
                                                (assignment) =>
                                                    assignment.recommendation ===
                                                    "Recommended"
                                            ).length
                                        }
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
                                        {
                                            assignments.filter(
                                                (assignment) =>
                                                    assignment.recommendation ===
                                                    "Moderately Recommended"
                                            ).length
                                        }
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