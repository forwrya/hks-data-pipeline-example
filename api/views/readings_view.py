"""
The View is our business logic layer. It deals with plain objects representing things we care about,
such as sensor readings, not raw HTTP requests (Routes) or database connections (Models).

Its responsibilities would include checking rules (e.g. "can this user upload sensor readings?"), 
transforming the raw data into the correct format, interacting with other Views 
(e.g. "does the sensor these readings are referring to exist?"), caching, etc.
"""

from fastapi import UploadFile, HTTPException
import pandas as pd

from typing import List, Dict, Any

from models.readings_model import ReadingsModel
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