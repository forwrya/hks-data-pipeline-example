"""
    In the Route, we would use Middleware and Dependencies to do standard checks like auth and rate limiting.
    We can also do some basic validation.

    Afterwards, the Route passes the request body along to the matching View to handle business logic, data transformation, caching, etc.
"""

from fastapi import APIRouter, UploadFile, HTTPException
from views.readings_view import ReadingsView

class ReadingsRoute:
    def __init__(self, view: ReadingsView) -> None:
        self.router = APIRouter()
        self.view = view

        self.router.add_api_route("/readings", self.upload_readings_csv, methods=["POST"])
        self.router.add_api_route("/readings/anomalies", self.get_anomalies, methods=["GET"])

    async def upload_readings_csv(self, file:UploadFile):
        """
        Upload a CSV file containing sensor readings.

        Args:
            file: An UploadFile representing the file received in the request.
        Returns:
            Response body with a count of the ingested readings:
            {
                new_readings_count: 5
            }
        """

        # Do some basic validation
        content_type = file.content_type
        if content_type is None or content_type != "text/csv":
            raise HTTPException(415, "'file' must be of type 'text/csv'")
        
        return {
            "new_readings_count": await self.view.ingest_csv_readings(file)
        }
    
    async def get_anomalies(self, sensor_id: str | None = None,
                                  starting_timestamp: str | None = None, 
                                  ending_timestamp: str | None = None):
        """
        Fetch anomalous sensor readings based on sensor_id and/or a range of timestamps.
        At least one filter must be provided.
        Args:
            sensor_id: The ID of a specific sensor to fetch anomalies from. Optional
            starting_timestamp: The oldest timestamp to filter anomalies by (inclusive). Optional
            ending_timestamp: The most recent timestamp to filter anomalies by (inclusive). Optional
        Returns:
            Response body with a list of readings (w/ anomaly information) matching the filters.
        """
        
        return await self.view.get_readings(sensor_id, starting_timestamp, ending_timestamp, anomalies_only=True)