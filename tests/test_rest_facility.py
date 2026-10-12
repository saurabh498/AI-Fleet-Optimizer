'''RestFacility entity + CSV importer tests.'''

import csv
from pathlib import Path

from fastapi.testclient import TestClient

from backend.database.connection import SessionLocal
from backend.main import app
from backend.models.rest_facility import RestFacility
from backend.services.rest_facility_import import DATA_DIR


client = TestClient(app)


def _login(email, password):
    r = client.post(
        '/auth/login', json={'email': email, 'password': password}
    )
    assert r.status_code == 200, r.text
    return r.json()['access_token']


def _hdr(token):
    return {'Authorization': f'Bearer {token}'}


def _write_csv(filename, rows):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename
    fieldnames = [
        'name', 'facility_type', 'latitude', 'longitude',
        'address', 'road_reference', 'available_amenities',
        'source_url', 'source_date', 'verification_status', 'notes',
    ]
    with path.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({**{k: '' for k in fieldnames}, **r})
    return path


def _cleanup(*filenames):
    for fn in filenames:
        p = DATA_DIR / fn
        if p.exists():
            p.unlink()
    db = SessionLocal()
    try:
        db.query(RestFacility).delete()
        db.commit()
    finally:
        db.close()


# -------------------------------------------------
# Importer — happy path
# -------------------------------------------------

def test_import_csv_creates_facilities():
    fn = 'test_happy.csv'
    _cleanup(fn)
    _write_csv(fn, [
        {
            'name': 'Test Facility A',
            'facility_type': 'apna_ghar',
            'latitude': '28.6139',
            'longitude': '77.2090',
            'source_url': 'https://example.invalid/test',
            'source_date': '2026-01-15',
            'verification_status': 'pending',
        },
        {
            'name': 'Test Facility B',
            'facility_type': 'wayside_amenity',
            'latitude': '19.0760',
            'longitude': '72.8777',
            'source_url': 'https://example.invalid/test',
            'source_date': '2026-01-15',
            'verification_status': 'pending',
        },
    ])

    token = _login('manager@fleetops.in', 'manager123')
    r = client.post(
        '/rest-facilities/import-csv',
        json={'filename': fn},
        headers=_hdr(token),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body['total_rows'] == 2
    assert body['created'] == 2
    assert body['rejected'] == []
    _cleanup(fn)


def test_import_csv_dedups_by_name_and_coords():
    fn = 'test_dedup.csv'
    _cleanup(fn)
    row = {
        'name': 'Test Dup Facility',
        'facility_type': 'apna_ghar',
        'latitude': '28.6139',
        'longitude': '77.2090',
        'source_url': 'https://example.invalid/test',
        'source_date': '2026-01-15',
        'verification_status': 'pending',
    }
    _write_csv(fn, [row, dict(row)])

    token = _login('manager@fleetops.in', 'manager123')
    r = client.post(
        '/rest-facilities/import-csv',
        json={'filename': fn},
        headers=_hdr(token),
    )
    body = r.json()
    assert body['created'] == 1
    assert body['skipped_duplicates'] == 1
    _cleanup(fn)


# -------------------------------------------------
# Importer — rejection paths
# -------------------------------------------------

def test_import_csv_rejects_missing_source_url():
    fn = 'test_no_source.csv'
    _cleanup(fn)
    _write_csv(fn, [{
        'name': 'Test No Source',
        'facility_type': 'apna_ghar',
        'latitude': '28.6139',
        'longitude': '77.2090',
        'source_url': '',
        'source_date': '2026-01-15',
        'verification_status': 'pending',
    }])
    token = _login('manager@fleetops.in', 'manager123')
    r = client.post(
        '/rest-facilities/import-csv',
        json={'filename': fn},
        headers=_hdr(token),
    )
    body = r.json()
    assert body['created'] == 0
    assert len(body['rejected']) == 1
    assert 'source_url' in body['rejected'][0]['reason']
    _cleanup(fn)


def test_import_csv_rejects_invalid_coordinates():
    fn = 'test_bad_coord.csv'
    _cleanup(fn)
    _write_csv(fn, [{
        'name': 'Test Bad Coord',
        'facility_type': 'apna_ghar',
        'latitude': '999',
        'longitude': '77.2090',
        'source_url': 'https://example.invalid/test',
        'source_date': '2026-01-15',
        'verification_status': 'pending',
    }])
    token = _login('manager@fleetops.in', 'manager123')
    r = client.post(
        '/rest-facilities/import-csv',
        json={'filename': fn},
        headers=_hdr(token),
    )
    body = r.json()
    assert body['created'] == 0
    assert 'coordinates' in body['rejected'][0]['reason']
    _cleanup(fn)


def test_import_csv_rejects_bad_status():
    fn = 'test_bad_status.csv'
    _cleanup(fn)
    _write_csv(fn, [{
        'name': 'Test Bad Status',
        'facility_type': 'apna_ghar',
        'latitude': '28.6',
        'longitude': '77.2',
        'source_url': 'https://example.invalid/test',
        'source_date': '2026-01-15',
        'verification_status': 'totally_made_up',
    }])
    token = _login('manager@fleetops.in', 'manager123')
    r = client.post(
        '/rest-facilities/import-csv',
        json={'filename': fn},
        headers=_hdr(token),
    )
    body = r.json()
    assert body['created'] == 0
    assert 'verification_status' in body['rejected'][0]['reason']
    _cleanup(fn)


def test_import_csv_handles_missing_file():
    token = _login('manager@fleetops.in', 'manager123')
    r = client.post(
        '/rest-facilities/import-csv',
        json={'filename': 'does_not_exist.csv'},
        headers=_hdr(token),
    )
    body = r.json()
    assert body['created'] == 0
    assert any('not found' in x['reason'] for x in body['rejected'])


# -------------------------------------------------
# RBAC
# -------------------------------------------------

def test_list_facilities_requires_auth():
    r = client.get('/rest-facilities/')
    assert r.status_code in (401, 403)


def test_driver_cannot_import():
    token = _login('driver@fleetops.in', 'driver123')
    r = client.post(
        '/rest-facilities/import-csv',
        json={'filename': 'template.csv'},
        headers=_hdr(token),
    )
    assert r.status_code == 403


def test_manager_can_list():
    token = _login('manager@fleetops.in', 'manager123')
    r = client.get('/rest-facilities/', headers=_hdr(token))
    assert r.status_code == 200
