"""
The View is our business logic layer. It deals with plain objects representing things we care about,
such as sensor readings, not raw HTTP requests (Routes) or database connections (Models).

Its responsibilities would include checking rules (e.g. "can this user upload sensor readings?"), 
transforming the raw data into the correct format, interacting with other Views 
(e.g. "does the sensor these readings are referring to exist?"), caching, etc.
"""

from fastapi import UploadFile, HTTPException
import pandas as pd

from typing import List, Dict, Any, Sequence
import dateutil
from datetime import datetime

from models.readings_model import ReadingsModel, SensorReading
from anomaly_detector import AnomalyDetector

class ReadingsView:
    def __init__(self, model: ReadingsModel) -> None:
        self.model = model

    async def ingest_csv_readings(self, csv: UploadFile) -> int:
        """
        Get the sensor readings out of a given csv file and store them in this system.

        Args:
            csv: An UploadFile containing sensor readings.
        Returns:
            The number of readings ingested.
        """
        # Try to parse the csv into a dict; throw an HTTP error response if it fails
        try:
            csv_dataframe = pd.read_csv(csv.file)
            destination: Dict[str, Any] = {}
            readings = csv_dataframe.to_dict(orient="records", into=destination)
        except:
            raise HTTPException(400, "CSV file is malformed.")
        
        # In a View, we can examine the parameters and make sure they make sense (e.g. "does the thing they're trying to update exist?")
        # Some constraints may be better (or at least more conveniently) left for the database schema to enforce (at the cost of good user feedback)
        # For now, we'll just make sure the csv has the minimum set of headers
        required_fields = set(["timestamp", "sensor_id", "temperature", "humidity", "pressure", "location"])
        missing_fields = required_fields.difference(csv_dataframe.columns.to_list())
        if missing_fields:
            raise HTTPException(400, f"CSV is missing one or more required columns: {[field for field in missing_fields]}")
        
        # Run the anomaly detection algorithm on the readings, modifying them in place
        self.append_anomaly_detections(readings)
        
        # Pass the readings along to the model to get sent to the database
        return await self.model.insert_readings(readings)

    def append_anomaly_detections(self, sensor_data: List[Dict[str, Any]]) -> None:
        """
        Apply the >2 stdev from the rolling mean anomaly detection algorithm to the given sensor readings.

        Ideally I would like to batch process this by having a queue of (sensor, date_range) jobs that will be
        consumed by multiple workers that will pull the data from the database, run the algorithm, and write the changes.
        For now, we'll just run the algorithm when we get new data before sending it to the database.

        Args:
            sensor_data: List of sensor reading dictionaries with keys:
                            id, timestamp, sensor_id, temperature, humidity, pressure, location
                
                        The list entries are modified with an anomalies key containing a list of objects with:
                            anomaly_type, confidence_score, detected_at
        """
        anomaly_detector = AnomalyDetector()

        anomalies = anomaly_detector.detect_anomalies(sensor_data)

        for anomaly in anomalies:
             # We can take advantage of the shared sort to convert the 1-indexed reading_id into a 0-indexed list index
            reading_to_update = sensor_data[anomaly["sensor_data_id"] - 1]

            if "anomalies" not in reading_to_update:
                reading_to_update["anomalies"] = []
            
            # Remove the unnecessary ID and add the new anomaly
            anomaly.pop("sensor_data_id")
            reading_to_update["anomalies"].append(anomaly)
        return
    
    def reading_transformer(self, database_reading: SensorReading) -> Dict[str, Any]:
        """
        Transforms the raw database output into the format expected by the public API.

        In this case, we'll just take out the internal reading_id and convert to plain python types.
        """
        return {
            "sensor_id": database_reading.sensor_id,
            "timestamp": database_reading.timestamp,
            "temperature": database_reading.temperature,
            "humidity": database_reading.humidity,
            "pressure": database_reading.pressure,
            "location": database_reading.location,
            "anomalies": database_reading.anomalies
        }
    
    async def get_readings(self, sensor_id: str | None = None,
                                 starting_timestamp: str | None = None, 
                                 ending_timestamp: str | None = None,
                                 anomalies_only: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch sensor readings based on one or more filters.
        At least one filter must be provided.

        This is where we would also want to implement pagination and a sort field.

        Args:
            sensor_id: The ID of a specific sensor to fetch anomalies from. Optional
            starting_timestamp: The oldest timestamp to filter anomalies by (inclusive). Optional
            ending_timestamp: The most recent timestamp to filter anomalies by (inclusive). Optional
            anomalies_only: Whether or not to filter to only readings marked as anomalies. Optional
        Returns:
            Response body with a list of readings (w/ anomaly information) matching the filters.
        """
        readings = []
        starting_datetime = None
        ending_datetime = None

        # Make sure we're using at least one filter so we're not requesting the entire table
        if all(reading_filter is None for reading_filter in [sensor_id, starting_timestamp, ending_timestamp]):
            raise HTTPException(400, "At least one filter must be provided.")

        # Validate the timestamps, if provided
        if starting_timestamp is not None:          
            try:
                starting_datetime = dateutil.parser.parse(starting_timestamp)
            except:
                raise HTTPException(400, "starting_timestamp is not a valid ISO date string.")
        
        if ending_timestamp is not None:          
            try:
                ending_datetime = dateutil.parser.parse(ending_timestamp)
            except:
                raise HTTPException(400, "ending_timestamp is not a valid ISO date string.")
            
        # If we're finding readings between a start and end time, make sure the end time is after the start
        if ending_datetime is not None and starting_datetime is not None:
            if ending_datetime < starting_datetime:
                raise HTTPException(400, "ending_timestamp must come after starting_timestamp")
            
        # TODO: Here we could use a cache (like Redis) to cache the readings with the filter(s) as cache keys
        
        # Cache miss, get from database
        readings = await self.model.get_readings(sensor_id, starting_datetime, ending_datetime, anomalies_only)

        # Clean up the raw data and return
        return [self.reading_transformer(reading) for reading in readings]