from backend.database.connection import SessionLocal
from backend.services.ml_decision_context import (
    build_ml_decision_context
)
from backend.services.assignment_decision import (
    generate_assignment_decision
)


db = SessionLocal()

truck_id = 2

print("=" * 60)
print("ML INTEGRATION AUDIT")
print("=" * 60)

print("\n1. ML DECISION CONTEXT")

context = build_ml_decision_context(
    truck_id,
    db
)

print(context)

print("\n2. ASSIGNMENT DECISION")

decision = generate_assignment_decision(
    truck_id,
    db
)

print(decision)

db.close()