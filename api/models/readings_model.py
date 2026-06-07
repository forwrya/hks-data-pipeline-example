"""
The Model's main purpose is to encapsulate database access. It should receive data ready to be written into
the database, or return data as it was represented in the database.

The actual connection to the database should be managed at a higher level and passed into the Model.

I've implemented this Model with an ORM for convenience's sake, but other implementations could easily
be slotted into the application by passing them to the corresponding View.
"""

from sqlalchemy import Column, BigInteger, Double, Text, TIMESTAMP, Identity
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from typing import List, Dict, Hashable, Any

import dateutil

class SensorReading(declarative_base()):
    __tablename__ = "readings"

    reading_id = Column(BigInteger, Identity(always=True), primary_key=True)
    sensor_id = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    temperature = Column(Double)
    humidity = Column(Double)
    pressure = Column(Double)
    location = Column(Text, nullable=False)


class ReadingsModel:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.session_maker = session_maker

    async def insert_readings(self, readings: List[Dict[Hashable, Any]]) -> int:
        """
        Bulk inserts readings into the database.

        Args:
            csv: An UploadFile containing sensor readings.
        Returns:
            The number of readings inserted.
        """
        new_readings_count = 0

        async with self.session_maker() as session:
            async with session.begin():
                # All or nothing. Eventually we might want to allow partial inserts and return the problematic rows as feedback to the user
                session.add_all([
                    SensorReading(
                        sensor_id = new_reading["sensor_id"],
                        timestamp = dateutil.parser.parse(new_reading["timestamp"]),
                        temperature = new_reading["temperature"],
                        humidity = new_reading["humidity"],
                        pressure = new_reading["pressure"],
                        location = new_reading["location"]
                    ) for new_reading in readings
                ])

        new_readings_count = len(readings)

        return new_readings_count
