from ortools.linear_solver import pywraplp


def optimize_assignments(candidates):
    """
    Optimize truck-load assignments using OR-Tools.

    Constraints:
    - One truck can receive at most one load.
    - One shipment can be assigned to at most one truck.

    Objective:
    - Maximize total decision score.
    """

    if not candidates:
        return []

    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        raise RuntimeError(
            "OR-Tools SCIP solver could not be created"
        )

    # -------------------------------------------------
    # Create binary decision variables
    # -------------------------------------------------
    variables = {}

    for index, candidate in enumerate(candidates):
        variables[index] = solver.BoolVar(
            f"assignment_{index}"
        )

    # -------------------------------------------------
    # Truck constraint
    # One truck -> maximum one shipment
    # -------------------------------------------------
    truck_ids = set(
        candidate["truck_id"]
        for candidate in candidates
    )

    for truck_id in truck_ids:

        truck_variables = [
            variables[index]
            for index, candidate in enumerate(candidates)
            if candidate["truck_id"] == truck_id
        ]

        solver.Add(
            solver.Sum(truck_variables) <= 1
        )

    # -------------------------------------------------
    # Shipment constraint
    # One shipment -> maximum one truck
    # -------------------------------------------------
    load_ids = set(
        candidate["load_id"]
        for candidate in candidates
    )

    for load_id in load_ids:

        load_variables = [
            variables[index]
            for index, candidate in enumerate(candidates)
            if candidate["load_id"] == load_id
        ]

        solver.Add(
            solver.Sum(load_variables) <= 1
        )

    objective = solver.Objective()

    for index, candidate in enumerate(candidates):

        decision_score = float(
    candidate.get(
        "ml_adjusted_decision_score",
        candidate.get(
            "decision_score",
            candidate.get(
                "match_score",
                0
            )
        )
    )
)

        route_efficiency = float(
            candidate.get(
                "route_efficiency_score",
                0
            )
        )

        profit = float(
            candidate.get(
                "estimated_route_profit",
                0
            )
        )

        route_cost = float(
            candidate.get(
                "estimated_route_cost",
                0
            )
        )

        # Normalize profit so that large rupee values
        # do not dominate the optimization.
        normalized_profit = min(
            max(profit / 500, 0),
            100
        )

        # Lower cost is better, therefore convert it
        # into a positive optimization component.
        cost_score = max(
            100 - (route_cost / 100),
            0
        )

        combined_score = (
            0.40 * decision_score
            + 0.25 * route_efficiency
            + 0.25 * normalized_profit
            + 0.10 * cost_score
        )

        candidate["optimization_score"] = round(
            combined_score,
            2
        )

        candidate["optimization_basis"] = {
            "decision_score_weight": 40,
            "route_efficiency_weight": 25,
            "profit_weight": 25,
            "cost_weight": 10,
        }

        objective.SetCoefficient(
            variables[index],
            combined_score
        )

    objective.SetMaximization()

    # -------------------------------------------------
    # Solve
    # -------------------------------------------------
    status = solver.Solve()

    if status not in (
        pywraplp.Solver.OPTIMAL,
        pywraplp.Solver.FEASIBLE
    ):
        return []

    # -------------------------------------------------
    # Extract selected assignments
    # -------------------------------------------------
    selected = []

    for index, candidate in enumerate(candidates):

        if variables[index].solution_value() > 0.5:
            selected.append(candidate)

    return selected