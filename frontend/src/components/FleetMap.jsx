import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
} from "react-leaflet";

import L from "leaflet";

import {
  getLatestTruckLocation,
  getRestFacilities,
} from "../services/api";


// Fix Leaflet default marker icons in Vite/React
// (still needed if any default markers are used elsewhere)
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});


// -------------------------------------------------
// Truck icon — emoji in a status-coloured ring
// -------------------------------------------------

const TRUCK_STATUS_COLORS = {
  available: "#12b76a",
  in_transit: "#175cd3",
  assigned: "#f79009",
  waiting: "#f59e0b",
};

function makeTruckIcon(status) {
  const color = TRUCK_STATUS_COLORS[status] || "#667085";
  return L.divIcon({
    className: "truck-marker",
    html:
      '<div class="truck-marker-inner" style="border-color:' +
      color +
      '">&#128667;</div>',
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
}


// -------------------------------------------------
// Facility icons
// -------------------------------------------------

const VERIFIED_FACILITY_ICON = L.divIcon({
  className: "rest-facility-marker verified",
  html: '<div class="rest-facility-marker-inner">&#127968;</div>',
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16],
});

const PENDING_FACILITY_ICON = L.divIcon({
  className: "rest-facility-marker pending",
  html: '<div class="rest-facility-marker-inner">&#127968;</div>',
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16],
});


function FleetMap({ trucks }) {
  const [locations, setLocations] = useState({});
  const [facilities, setFacilities] = useState([]);

  // Poll truck locations
  useEffect(() => {
    const loadLocations = async () => {
      const locationData = {};

      for (const truck of trucks) {
        try {
          const location = await getLatestTruckLocation(
            truck.truck_id
          );

          if (
            location &&
            location.latitude != null &&
            location.longitude != null
          ) {
            locationData[truck.truck_id] = location;
          }
        } catch (error) {
          console.error(
            "Failed to load location for Truck #" +
              truck.truck_id +
              ":",
            error
          );
        }
      }

      setLocations(locationData);
    };

    if (trucks.length === 0) {
      return;
    }

    loadLocations();

    const interval = setInterval(loadLocations, 5000);

    return () => {
      clearInterval(interval);
    };
  }, [trucks]);

  // Load rest facilities once on mount
  useEffect(() => {
    const loadFacilities = async () => {
      try {
        const data = await getRestFacilities();
        setFacilities(data);
      } catch (error) {
        console.error("Failed to load rest facilities:", error);
      }
    };

    loadFacilities();
  }, []);

  const firstLocation = Object.values(locations)[0];

  const center = firstLocation
    ? [firstLocation.latitude, firstLocation.longitude]
    : [19.076, 72.8777];

  const verifiedCount = facilities.filter(
    (f) => f.verification_status === "verified"
  ).length;

  const pendingCount = facilities.filter(
    (f) => f.verification_status === "pending"
  ).length;

  return (
    <div className="fleet-map-wrapper">
      <MapContainer
        center={center}
        zoom={6}
        scrollWheelZoom={true}
        className="fleet-map"
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Truck markers */}

        {trucks.map((truck) => {
          const location = locations[truck.truck_id];

          if (!location) {
            return null;
          }

          return (
            <Marker
              key={"truck-" + truck.truck_id}
              position={[location.latitude, location.longitude]}
              icon={makeTruckIcon(truck.status)}
            >
              <Popup>
                <div className="truck-popup">
                  <strong>
                    &#128667; Truck #{truck.truck_id}
                  </strong>

                  <p>
                    <b>Type:</b> {truck.truck_type}
                  </p>
                  <p>
                    <b>Capacity:</b> {truck.capacity} kg
                  </p>
                  <p>
                    <b>City:</b>{" "}
                    {truck.current_city || "Unknown"}
                  </p>
                  <p>
                    <b>Status:</b> {truck.status}
                  </p>
                  <p>
                    <b>Latitude:</b> {location.latitude}
                  </p>
                  <p>
                    <b>Longitude:</b> {location.longitude}
                  </p>
                  <p>
                    <b>Last Update:</b>{" "}
                    {location.timestamp
                      ? new Date(
                          location.timestamp
                        ).toLocaleString()
                      : "Unknown"}
                  </p>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Rest facility markers */}

        {facilities.map((facility) => {
          if (
            facility.latitude == null ||
            facility.longitude == null
          ) {
            return null;
          }

          const isVerified =
            facility.verification_status === "verified";

          return (
            <Marker
              key={"facility-" + facility.facility_id}
              position={[facility.latitude, facility.longitude]}
              icon={
                isVerified
                  ? VERIFIED_FACILITY_ICON
                  : PENDING_FACILITY_ICON
              }
            >
              <Popup>
                <div className="facility-popup">
                  <strong>{facility.name}</strong>

                  <p>
                    <b>Type:</b>{" "}
                    {String(facility.facility_type).replace(
                      /_/g,
                      " "
                    )}
                  </p>

                  <p>
                    <b>Status:</b>{" "}
                    <span
                      className={
                        "facility-popup-status " +
                        facility.verification_status
                      }
                    >
                      {facility.verification_status}
                    </span>
                  </p>

                  {facility.road_reference && (
                    <p>
                      <b>Road:</b> {facility.road_reference}
                    </p>
                  )}

                  {facility.address && (
                    <p>
                      <b>Address:</b> {facility.address}
                    </p>
                  )}

                  {facility.available_amenities && (
                    <p>
                      <b>Amenities:</b>{" "}
                      {facility.available_amenities}
                    </p>
                  )}

                  <p>
                    <b>Source:</b>{" "}
                    <a
                      href={facility.source_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {facility.source_url.length > 45
                        ? facility.source_url.slice(0, 45) + "\u2026"
                        : facility.source_url}
                    </a>
                  </p>

                  <p>
                    <b>Source date:</b> {facility.source_date}
                  </p>

                  <p className="facility-popup-note">
                    Verified status is set by a human reviewer,
                    not automatically.
                  </p>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Legend */}

      {(verifiedCount > 0 || pendingCount > 0) && (
        <div className="map-legend">
          <div className="map-legend-title">Map Legend</div>

          <div className="map-legend-item">
            <span className="map-legend-icon truck">&#128667;</span>
            <span>Trucks</span>
          </div>

          <div className="map-legend-item">
            <span className="map-legend-icon facility-verified">
              &#127968;
            </span>
            <span>Verified facility ({verifiedCount})</span>
          </div>

          <div className="map-legend-item">
            <span className="map-legend-icon facility-pending">
              &#127968;
            </span>
            <span>Pending facility ({pendingCount})</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default FleetMap;
