from generate_data import DataGenerator, save_to_csv

import pytest
import os
import pandas as pd

@pytest.mark.parametrize("n", [5, 10, 100])
def test_should_generate_correct_number_of_readings(n):
    test_generator = DataGenerator()

    test_dataset = test_generator.generate_dataset(n)

    assert len(test_dataset) == n

@pytest.mark.parametrize("n, expected_exception", [(0, ZeroDivisionError), (1, ZeroDivisionError), ("100", TypeError)])
def test_should_fail_to_generate_bad_numbers_of_readings(n, expected_exception):
    test_generator = DataGenerator()

    with pytest.raises(expected_exception):
        test_generator.generate_dataset(n)

def test_should_sort_readings_from_oldest_to_newest():
    test_generator = DataGenerator()

    test_dataset = test_generator.generate_dataset(100)

    for previous_index, item in enumerate(test_dataset[1:]):
        current = item["timestamp"]
        previous = test_dataset[previous_index]["timestamp"]
        
        # Time zone should be constant, so just compare as ISO strings
        assert current > previous

test_csv_file = "./test_csv.csv"

@pytest.fixture()
def csv_test_fixture():
    # Make sure the environment is clean before the test
    try:
        os.remove(test_csv_file)
    except:
        pass

    yield

def test_should_write_readings_to_csv(csv_test_fixture):
    test_generator = DataGenerator()

    expected_dataset = test_generator.generate_dataset(100)

    save_to_csv(expected_dataset, test_csv_file)

    csv_dataframe = pd.read_csv(test_csv_file)
    actual_dataset = csv_dataframe.to_dict(orient="records")
    
    assert len(expected_dataset) == len(actual_dataset)

    # Check that readings were written to csv in sorted order
    for index in range(len(expected_dataset)):
        assert expected_dataset[index] == pytest.approx(actual_dataset[index])