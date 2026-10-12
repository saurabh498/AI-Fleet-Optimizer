'''
CSV import for rest facilities.

Every row is validated. Any row missing source_url, source_date,
valid coordinates, or a known type/status is REJECTED. Nothing is
inserted unless it passes all checks.

Duplicate rule: same (name, latitude, longitude) is skipped.
'''

import csv
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from backend.models.rest_facility import RestFacility
from backend.schemas.rest_facility import (
    FACILITY_TYPES,
    VERIFICATION_STATUSES,
)


DATA_DIR = Path('data/rest_facilities')

REQUIRED_COLUMNS = {
    'name',
    'facility_type',
    'latitude',
    'longitude',
    'source_url',
    'source_date',
    'verification_status',
}

OPTIONAL_COLUMNS = {
    'address',
    'road_reference',
    'available_amenities',
    'notes',
}


def _parse_date(raw: str) -> date | None:
    raw = (raw or '').strip()
    if not raw:
        return None
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _validate_row(row: dict, index: int) -> tuple[dict | None, dict | None]:
    '''Return (clean_row, rejection). Exactly one is None.'''
    name = (row.get('name') or '').strip()
    if not name:
        return None, {'row': index, 'reason': 'missing name'}

    ftype = (row.get('facility_type') or '').strip()
    if ftype not in FACILITY_TYPES:
        return None, {
            'row': index,
            'reason': f'invalid facility_type: {ftype!r}',
        }

    try:
        lat = float((row.get('latitude') or '').strip())
        lon = float((row.get('longitude') or '').strip())
    except (ValueError, TypeError):
        return None, {'row': index, 'reason': 'invalid coordinates'}

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return None, {'row': index, 'reason': 'coordinates out of range'}

    source_url = (row.get('source_url') or '').strip()
    if not source_url:
        return None, {'row': index, 'reason': 'missing source_url'}

    source_date = _parse_date(row.get('source_date') or '')
    if source_date is None:
        return None, {
            'row': index,
            'reason': 'missing or unparseable source_date',
        }

    status = (row.get('verification_status') or '').strip().lower()
    if status not in VERIFICATION_STATUSES:
        return None, {
            'row': index,
            'reason': f'invalid verification_status: {status!r}',
        }

    return {
        'name': name,
        'facility_type': ftype,
        'latitude': lat,
        'longitude': lon,
        'address': (row.get('address') or '').strip() or None,
        'road_reference': (row.get('road_reference') or '').strip() or None,
        'available_amenities': (
            row.get('available_amenities') or ''
        ).strip() or None,
        'source_url': source_url,
        'source_date': source_date,
        'verification_status': status,
        'notes': (row.get('notes') or '').strip() or None,
    }, None


def import_csv(filename: str, db: Session) -> dict:
    '''
    Import a CSV from data/rest_facilities/<filename>.
    Path is confined to DATA_DIR to prevent traversal.
    '''
    safe_name = Path(filename).name
    path = DATA_DIR / safe_name

    if not path.exists() or not path.is_file():
        return {
            'file': safe_name,
            'total_rows': 0,
            'created': 0,
            'skipped_duplicates': 0,
            'rejected': [
                {'row': 0, 'reason': f'file not found: {safe_name}'}
            ],
        }

    created = 0
    skipped = 0
    rejected: list[dict] = []
    total = 0

    with path.open('r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            return {
                'file': safe_name,
                'total_rows': 0,
                'created': 0,
                'skipped_duplicates': 0,
                'rejected': [
                    {
                        'row': 0,
                        'reason': f'missing columns: {sorted(missing)}',
                    }
                ],
            }

        for i, raw_row in enumerate(reader, start=1):
            total += 1
            clean, rejection = _validate_row(raw_row, i)
            if rejection:
                rejected.append(rejection)
                continue

            exists = (
                db.query(RestFacility)
                .filter(
                    RestFacility.name == clean['name'],
                    RestFacility.latitude == clean['latitude'],
                    RestFacility.longitude == clean['longitude'],
                )
                .first()
            )
            if exists:
                skipped += 1
                continue

            db.add(RestFacility(**clean))
            # Force the INSERT so subsequent iterations see this row
            # when checking for in-file duplicates.
            db.flush()
            created += 1

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        rejected.append({'row': 0, 'reason': f'commit failed: {exc}'})

    return {
        'file': safe_name,
        'total_rows': total,
        'created': created,
        'skipped_duplicates': skipped,
        'rejected': rejected,
    }
