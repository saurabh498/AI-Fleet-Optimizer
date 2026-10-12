# Pending NHAI WSA Sites — Need Coordinates

Source: Lok Sabha Unstarred Question No. 2420, answered 03 Aug 2023
PDF: https://sansad.in/getFile/loksabhaquestions/annex/1712/AU2420.pdf

Each row below is a WSA site the government reported as **operational**.
Only **descriptions and chainage** are published — no GPS. Coordinates
must be sourced individually before importing.

Format: `S.No | State | NH | Description`

## Haryana
1.  Haryana   NH-148B  Narnaul Bypass Crossing - Paniyala Mor / NH-148B/15+000/LHS/Mahendragarh
2.  Haryana   Delhi-Mumbai  DD2-3L_Package3_63+140 LHS
3.  Haryana   Delhi-Mumbai  DD2-4R_Package3_69+900 RHS
8.  Haryana   Trans-Haryana  AK1-1L_Package1_21+100 LHS
9.  Haryana   Trans-Haryana  AK1-2R_Package1_21+100 RHS
10. Haryana   Trans-Haryana  AK1-3L_Package2_50+650 LHS
11. Haryana   Trans-Haryana  AK1-4R_Package2_50+650 RHS
12. Haryana   Trans-Haryana  AK2-5L_Package4_93+530 LHS
13. Haryana   Trans-Haryana  AK2-6R_Package4_93+530 RHS
14. Haryana   Trans-Haryana  AK2-7L_Package5_120+400 LHS
15. Haryana   Trans-Haryana  AK2-8R_Package5_120+400 RHS
16. Haryana   Trans-Haryana  AK3-9L_Package6_152+500 LHS
17. Haryana   Trans-Haryana  AK3-10R_Package6_152+500 RHS
18. Haryana   Trans-Haryana  AK3-11L_Package7_191+600 LHS
19. Haryana   Trans-Haryana  AK3-12R_Package7_191+600 RHS

## Uttar Pradesh
20. Uttar Pradesh  NE2  Kundli-Palwal / NE2_39+500_RHS_Milak Chakarpur_Ghaziabad
21. Uttar Pradesh  NE3  UP/DME/01 Ghaziabad
22. Uttar Pradesh  NE3  UP/DME/02 Ghaziabad_36+250 RHS
23. Uttar Pradesh  NE2  Kundli-Palwal / NE2_39+500_LHS_Milak Chakarpur_Ghaziabad
24. Uttar Pradesh  NH-27  Jhansi-Orai / NH-27/123/RHS/UP West
25. Uttar Pradesh  NH-19  Kurgaon, Allahabad Bypass

## Andhra Pradesh
26. Andhra Pradesh  NH-16  Gowravaram/AP
27. Andhra Pradesh  NH-716  Vallur/AP
28. Andhra Pradesh  NH-135  Anantapur-Bangalore / NH7/387+388/LHS/Anantapur District

## Karnataka / Tamil Nadu
29. Karnataka  NH-40  NH04_46.700+46.900_LHS_Yedehalli_Karnataka
30. Tamil Nadu  NH-135  NH7/61+130/LHS/Chinnar/Krishnagiri

## West Bengal
31. West Bengal  NH-19  Govindpur
32. West Bengal  NH-19  Budbud

## Gujarat
33. Gujarat  NH-27  NE-1/23km to 24km/RHS/Makwa/Ahmedabad
34. Gujarat  NH-27  NE-1/78km to 79km/LHS/Poicha/Vadodara

## Madhya Pradesh
35. Madhya Pradesh  NH-60  Indore-Khalaghat/NH-3/63+300/RHS/Dhar District
36. Madhya Pradesh  NH-27  Baran-Shivpuri-Jhansi/NH-27/1227+200/LHS/Gwalior
37. Madhya Pradesh  NH-27  Baran-Shivpuri-Jhansi/1194+300/RHS/Gwalior
38. Madhya Pradesh  NH-46  Shivpuri-Guna
39. Madhya Pradesh  NH-319  NH-30_358+100_RHS_Madanpura

## Rajasthan
40. Rajasthan  Delhi-Mumbai  DD4-6L_Package6_172+550 LHS
41. Rajasthan  Delhi-Mumbai  DD4-6R_Package6_172+550 RHS
42. Rajasthan  NH-48  NH-48/20.057+20.357/RHS/Srigovindpura, Jaipur
43. Rajasthan  NH-48  NH-48/20+432 to 20+732/LHS/Bilouchi, Jaipur Bypass

## How to look up coordinates for each site

The description format gives you a **road + chainage + side** which is
more precise than a city name. Options:

1. **Chainage lookup** — the km marker (e.g., "63+140") maps to a
   physical km post on that highway. Use OpenStreetMap or Google Maps
   on the NH, find the km marker, drop a pin.
2. **NHAI site-specific RFP** — every tendered site has its own RFP
   with a "GPS Latitude / GPS Longitude" row (as the Assam one did).
   Search "NHAI WSA RFP <site code>".
3. **District + road reference** — if you can't get the km marker,
   geocode the district + national highway, then refine by village
   name where available.

**Never invent a coordinate to fill the row.** If you can't source it,
leave the row out and note it here.

## Suggested columns when you populate them

    name,facility_type,latitude,longitude,address,road_reference,available_amenities,source_url,source_date,verification_status,notes

- `facility_type` = `wayside_amenity` for all these
- `verification_status` = `pending` initially
- `source_url` = the specific page or PDF you read
- `source_date` = today's date
- `notes` = "Lok Sabha 2420 / Annexure I (03 Aug 2023). Operational per ministry reply."

Once you have 3-5 sites imported, we can add map markers (Stage 5).
