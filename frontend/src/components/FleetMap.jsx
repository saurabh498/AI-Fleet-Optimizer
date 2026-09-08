import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
} from "react-leaflet";

import { useEffect, useState } from "react";

import L from "leaflet";

import {
  getLatestTruckLocation,
} from "../services/api";

// Fix Leaflet default marker icons in Vite/React
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function FleetMap({ trucks }) {
  const [locations, setLocations] = useState({});

  useEffect(() => {
    const loadLocations = async () => {
      const locationData = {};

      for (const truck of trucks) {
        try {
          const location =
            await getLatestTruckLocation(
              truck.truck_id
            );

          if (
            location &&
            location.latitude != null &&
            location.longitude != null
          ) {
            locationData[truck.truck_id] =
              location;
          }
        } catch (error) {
          console.error(
            `Failed to load location for Truck #${truck.truck_id}:`,
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

    const interval = setInterval(
      loadLocations,
      5000
    );

    return () => {
      clearInterval(interval);
    };
  }, [trucks]);

  const firstLocation =
    Object.values(locations)[0];

  const center = firstLocation
    ? [
      firstLocation.latitude,
      firstLocation.longitude,
    ]
    : [19.076, 72.8777];

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

        {trucks.map((truck) => {
          const location =
            locations[truck.truck_id];

          if (!location) {
            return null;
          }

          return (
            <Marker
              key={truck.truck_id}
              position={[
                location.latitude,
                location.longitude,
              ]}
            >

              <Popup>

                <div className="truck-popup">

                  <strong>
                    🚛 Truck #{truck.truck_id}
                  </strong>

                  <p>
                    <b>Type:</b>{" "}
                    {truck.truck_type}
                  </p>

                  <p>
                    <b>Capacity:</b>{" "}
                    {truck.capacity} kg
                  </p>

                  <p>
                    <b>City:</b>{" "}
                    {truck.current_city ||
                      "Unknown"}
                  </p>

                  <p>
                    <b>Status:</b>{" "}
                    {truck.status}
                  </p>

                  <p>
                    <b>Latitude:</b>{" "}
                    {location.latitude}
                  </p>

                  <p>
                    <b>Longitude:</b>{" "}
                    {location.longitude}
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

      </MapContainer>

    </div>
  );
}

export default FleetMap;