"""
The View is easy to unit test because just have to stub/mock the corresponding Model,
not any HTTP or Database related classes.

Tests at the other layers are better suited in my experience to "integration" testing,
where the tests send actual HTTP requests and the environment is configured to use a SQLite
or other simple database.
"""
import pytest
from unittest.mock import Mock, AsyncMock

from views.readings_view import ReadingsView
from samples.generate_data import DataGenerator, save_to_csv

from fastapi import UploadFile, HTTPException
from io import BytesIO
import os
import pandas as pd

@pytest.fixture()
def default_test_model():
    test_model = AsyncMock()
    return test_model

@pytest.mark.asyncio
async def test_should_return_error_when_file_is_empty(default_test_model):
    test_view = ReadingsView(default_test_model)
    empty_test_file = UploadFile(BytesIO())

    with pytest.raises(HTTPException) as exception:
        await test_view.ingest_csv_readings(empty_test_file)
    
    assert exception.value.status_code == 400

test_csv_filename = "./test_csv.csv"

@pytest.fixture()
def csv_test_fixture():
    # Make sure the environment is clean before the test
    try:
        os.remove(test_csv_filename)
    except:
        pass

    yield

@pytest.mark.parametrize("included_headers, missing_headers", [
    ([], ["id", "timestamp", "sensor_id", "temperature", "humidity", "pressure", "location"]),
    (["timestamp"], ["id", "sensor_id", "temperature", "humidity", "pressure", "location"]),
    (["id", "timestamp", "sensor_id", "temperature", "humidity", "location"], ["pressure"])
    ])
@pytest.mark.asyncio
async def test_should_return_error_when_headers_are_wrong(default_test_model, csv_test_fixture, included_headers, missing_headers):
    test_view = ReadingsView(default_test_model)

    test_dataframe = pd.DataFrame(columns=included_headers)
    test_dataframe.to_csv(test_csv_filename)

    test_file = UploadFile(open(test_csv_filename, "rb"))

    with pytest.raises(HTTPException) as exception:
        await test_view.ingest_csv_readings(test_file)
    
    assert exception.value.status_code == 400

    for header in missing_headers:
        assert header in str(exception.value)

@pytest.fixture()
def clean_readings_file_fixture(csv_test_fixture):
    test_generator = DataGenerator()

    expected_dataset = test_generator.generate_dataset(5)

    save_to_csv(expected_dataset, test_csv_filename)

    return expected_dataset

@pytest.fixture()
def anomalous_readings_file_fixture(csv_test_fixture):
    test_generator = DataGenerator(anomaly_rate=.9)

    expected_dataset = test_generator.generate_dataset(100)

    save_to_csv(expected_dataset, test_csv_filename)

    return expected_dataset

@pytest.mark.asyncio
async def test_should_pass_readings_to_model(default_test_model, clean_readings_file_fixture):
    test_view = ReadingsView(default_test_model)
    test_file = UploadFile(open(test_csv_filename, "rb"))

    await test_view.ingest_csv_readings(test_file)

    default_test_model.insert_readings.assert_awaited_once()
    default_test_model.insert_readings.assert_called_once_with(clean_readings_file_fixture)

@pytest.mark.asyncio
async def test_should_pass_readings_and_anomalies_to_model(default_test_model, anomalous_readings_file_fixture):
    test_view = ReadingsView(default_test_model)
    test_file = UploadFile(open(test_csv_filename, "rb"))

    await test_view.ingest_csv_readings(test_file)

    default_test_model.insert_readings.assert_awaited_once()
    default_test_model.insert_readings.assert_called_once()

    actual_readings = default_test_model.insert_readings.call_args.args[0]

    # Doing this well would probably require mocking out the anomaly detector, so for now just make sure some anomalies got added
    anomaly_count = 0
    for actual_reading in actual_readings:
        print(actual_reading)
        if "anomalies" in actual_reading:
            anomaly_count += len(actual_reading["anomalies"])

    assert anomaly_count > 0