'''Create demo drivers (idempotent).'''

from backend.database.connection import SessionLocal
from backend.models.driver import Driver


DEMO_DRIVERS = [
    {'display_name': 'Ravi Kumar',   'availability_status': 'available'},
    {'display_name': 'Anil Sharma',  'availability_status': 'on_duty'},
    {'display_name': 'Priya Verma',  'availability_status': 'available'},
]


def main():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for spec in DEMO_DRIVERS:
            existing = db.query(Driver).filter(
                Driver.display_name == spec['display_name']
            ).first()
            if existing:
                skipped += 1
                continue
            db.add(Driver(**spec))
            created += 1
        db.commit()
        print(f'Drivers created: {created}, skipped: {skipped}')
    finally:
        db.close()


if __name__ == '__main__':
    main()
