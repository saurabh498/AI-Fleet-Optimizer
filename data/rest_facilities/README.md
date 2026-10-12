# Rest Facility Data — Sourcing Guide

This folder holds **CSV imports** for the est_facilities table.
Every row must be traceable to a real, publicly verifiable source.

## Required columns

| Column | Notes |
|---|---|
| 
ame | Facility name as published by the source |
| acility_type | One of: pna_ghar, wayside_amenity, other_verified |
| latitude | Decimal degrees, from the source — **do not invent** |
| longitude | Decimal degrees, from the source — **do not invent** |
| source_url | Direct link to the page/document where this is published |
| source_date | Date you retrieved it (YYYY-MM-DD) |
| erification_status | One of: pending, erified, etired |

## Optional columns

- ddress
- oad_reference (e.g. NH-48)
- vailable_amenities (comma-separated: parking,toilets,dormitory,food)
- 
otes

## Suggested sources

- **Apna Ghar** (MoRTH trucking amenity programme):
  https://morth.nic.in/
- **Wayside Amenities** (NHAI):
  https://nhai.gov.in/
- State transport department pages

Look for PDFs or HTML pages that list the facility name and location.
For each, record the URL as source_url and the date you read it.

## ⚠️ Honesty rules

- **Do not** invent coordinates. If a source only gives a city, either
  find a more precise source or leave the row out.
- **Do not** claim a facility has vacant parking / dormitory unless a
  live, reliable source confirms it. Leave vailable_amenities blank
  if unknown.
- **Do not** set erification_status = verified until a human has
  manually cross-checked the row.
- If the source uses a different facility-type label, use
  other_verified and describe it in 
otes.

## How to import

1. Copy 	emplate.csv to a new file (e.g. 
h48_2026-10.csv).
2. Fill rows with data from documented sources.
3. Place the file in this folder.
4. Call the import endpoint as a manager or admin:


Or use Swagger UI at http://localhost:8000/docs.

5. Review the response — rejected rows list a reason for each.

## Verification workflow

New imports land as erification_status = pending unless the CSV
explicitly says erified. A human should review pending rows before
the decision engine treats them as trusted.
