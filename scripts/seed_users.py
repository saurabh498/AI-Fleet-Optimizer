'''Create default demo users (idempotent).'''

from backend.database.connection import SessionLocal
from backend.models.user import User
from backend.services.auth import hash_password


DEFAULT_USERS = [
    {
        "email": "admin@fleetops.in",
        "full_name": "Fleet Admin",
        "password": "admin123",
        "role": "admin",
    },
    {
        "email": "manager@fleetops.in",
        "full_name": "Fleet Manager",
        "password": "manager123",
        "role": "manager",
    },
    {
        "email": "driver@fleetops.in",
        "full_name": "Fleet Driver",
        "password": "driver123",
        "role": "driver",
    },
]


def main():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for spec in DEFAULT_USERS:
            existing = db.query(User).filter(User.email == spec["email"]).first()
            if existing:
                skipped += 1
                continue
            db.add(
                User(
                    email=spec["email"],
                    full_name=spec["full_name"],
                    hashed_password=hash_password(spec["password"]),
                    role=spec["role"],
                    is_active=True,
                )
            )
            created += 1
        db.commit()
        print(f"Users created: {created}, skipped (already exist): {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
