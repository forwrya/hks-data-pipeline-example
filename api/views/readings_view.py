"""
The View is our business logic layer. It deals with plain objects representing things we care about,
such as sensor readings, not raw HTTP requests (Routes) or database connections (Models).

Its responsibilities would include checking rules (e.g. "can this user upload sensor readings?"), 
transforming the raw data into the correct format, interacting with other Views 
(e.g. "does the sensor these readings are referring to exist?"), caching, etc.
"""

from fastapi import UploadFile, HTTPException
import pandas as pd

from models.readings_model import ReadingsModel

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
            readings = csv_dataframe.to_dict(orient="records")
        except:
            raise HTTPException(400, "CSV file is malformed.")
        
        # In a View, we can examine the parameters and make sure they make sense (e.g. "does the thing they're trying to update exist?")
        # Some constraints may be better (or at least more conveniently) left for the database schema to enforce (at the cost of good user feedback)
        # For now, we'll just make sure the csv has the minimum set of headers
        required_fields = set(["timestamp", "sensor_id", "temperature", "humidity", "pressure", "location"])
        missing_fields = required_fields.difference(csv_dataframe.columns.to_list())
        if missing_fields:
            raise HTTPException(400, f"CSV is missing one or more required columns: {[field for field in missing_fields]}")
        
        # Pass the readings along to the model to get sent to the database
        return await self.model.insert_readings(readings)
