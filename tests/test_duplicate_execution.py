from backend.database.connection import get_db
from backend.services.fleet_assignment_executor import execute_fleet_assignments


db = next(get_db())

recommendations = [
    {
        "truck_id": 2,
        "load_id": 16,
        "match_score": 200,
        "estimated_distance": 120.15,
        "estimated_route_cost": 3003.75,
        "estimated_route_profit": 26996.25,
        "recommendation": "Highly Recommended",
        "optimization_score": 124.15
    }
]

result = execute_fleet_assignments(
    db,
    recommendations
)

print("\n===== DUPLICATE EXECUTION TEST =====")
print(result)

db.close()