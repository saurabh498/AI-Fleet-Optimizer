import { useEffect, useState } from "react";

import {
  getLatestTruckLocation,
} from "../services/api";

function FleetStatus({ trucks }) {
  const [locations, setLocations] = useState({});
  const [lastUpdated, setLastUpdated] =
    useState(null);

  useEffect(() => {
    const loadLocations = async () => {
      const locationData = {};

      for (const truck of trucks) {
        try {
          const location =
            await getLatestTruckLocation(
              truck.truck_id
            );

          if (location) {
            locationData[truck.truck_id] =
              location;
          }
        } catch (error) {
          console.error(
            `Failed to load Truck #${truck.truck_id}`,
            error
          );
        }
      }

      setLocations(locationData);
      setLastUpdated(new Date());
    };

    if (trucks.length > 0) {
      loadLocations();
    }

    const interval = setInterval(
      loadLocations,
      5000
    );

    return () => {
      clearInterval(interval);
    };
  }, [trucks]);

  return (
    <div className="fleet-status-panel">

      <div className="fleet-status-header">

        <div>
          <h3>Live Fleet Status</h3>
          <p>
            Real-time truck location and status
          </p>
        </div>

        <div className="map-live-status">
          <span className="status-dot"></span>
          LIVE
        </div>

      </div>

      {lastUpdated && (
        <p className="fleet-last-updated">
          Last updated:{" "}
          {lastUpdated.toLocaleTimeString()}
        </p>
      )}

      <div className="fleet-status-table-wrapper">

        <table className="fleet-status-table">

          <thead>
            <tr>
              <th>Truck</th>
              <th>Location</th>
              <th>Status</th>
              <th>Destination</th>
              <th>Latitude</th>
              <th>Longitude</th>
            </tr>
          </thead>

          <tbody>

            {trucks.map((truck) => {
              const location =
                locations[truck.truck_id];

              return (
                <tr key={truck.truck_id}>

                  <td>
                    <strong>
                      🚛 Truck #{truck.truck_id}
                    </strong>
                  </td>

                  <td>
                    {truck.current_city ||
                      "Unknown"}
                  </td>

                  <td>
                    <span
                      className={`fleet-status-badge ${String(
                        truck.status || ""
                      )
                        .toLowerCase()
                        .replace(
                          /\s+/g,
                          "-"
                        )}`}
                    >
                      {truck.status ||
                        "Unknown"}
                    </span>
                  </td>

                  <td>
                    {truck.destination ||
                      "—"}
                  </td>

                  <td>
                    {location?.latitude ??
                      "—"}
                  </td>

                  <td>
                    {location?.longitude ??
                      "—"}
                  </td>

                </tr>
              );
            })}

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default FleetStatus;