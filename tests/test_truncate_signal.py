"""
Module: test_truncate_signal
Description: This module contains unit tests for the functions
in the truncate_signal module.
"""

import csv
import os
import unittest
from tempfile import NamedTemporaryFile

import numpy as np
import pandas as pd

from path_utils import extend_sys_path

with extend_sys_path(os.path.join("workflow", "scripts")):
    from truncate_signal import main


class TestTruncateSignal(unittest.TestCase):
    """
    Test suite for the functions in the truncate_signal module.
    """

    def setUp(self):
        """
        Set up the test environment by initializing a list to hold
        temporary file paths.
        """
        self.temp_files = []

    def tearDown(self):
        """
        Clean up the test environment by removing all temporary files
        created during the tests.
        """
        for file in self.temp_files:
            if os.path.exists(file):
                os.remove(file)

    def create_temp_feather_file(self, data):
        """
        Create a temporary Feather file from the provided data and
        return its file path.

        Parameters:
            data (dict): The data to write to the Feather file.

        Returns:
            str: The path to the created Feather file.
        """
        temp_file = NamedTemporaryFile(delete=False, suffix=".feather")
        temp_file.close()
        df = pd.DataFrame(data)
        df.to_feather(temp_file.name)
        self.temp_files.append(temp_file.name)
        return temp_file.name

    def create_temp_csv_file(self, data):
        """
        Create a temporary CSV file from the provided data and
        return its file path.

        Parameters:
            data (dict): The data to write to the CSV file.

        Returns:
            str: The path to the created CSV file.
        """
        temp_file = NamedTemporaryFile(delete=False, suffix=".csv")
        temp_file.close()
        with open(temp_file.name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['signal', 'size'])
            for signal, size in zip(data['signal'], data['size']):
                writer.writerow([signal, size])
        self.temp_files.append(temp_file.name)
        return temp_file.name

    def test_basic_functionality(self):
        """
        Test the main function with basic input data.

        Verifies that all signals in the output have the same
        truncated length.
        """
        input_data = {
            "signal": [
                [1, 2, 3, 4, 5],
                [6, 7, 8],
                [9, 10, 11, 12]
            ],
            "size": [5, 3, 4]
        }
        input_file = self.create_temp_feather_file(input_data)
        output_file = self.create_temp_feather_file({})

        main(input_file, output_file)

        df_output = pd.read_feather(output_file)
        self.assertTrue(
            all(len(signal) == 3 for signal in df_output['signal']))
        self.assertTrue(all(df_output['size'] == 3))

    def test_signals_of_different_lengths(self):
        """
        Test the main function with signals of different lengths.

        Verifies that all signals in the output are truncated to the
        shortest signal length.
        """
        input_data = {
            "signal": [
                [1, 2, 3, 4, 5],
                [6, 7],
                [8, 9, 10, 11, 12, 13]
            ],
            "size": [5, 2, 6]
        }
        input_file = self.create_temp_feather_file(input_data)
        output_file = self.create_temp_feather_file({})

        main(input_file, output_file)

        df_output = pd.read_feather(output_file)
        self.assertTrue(
            all(len(signal) == 2 for signal in df_output['signal']))
        self.assertTrue(all(df_output['size'] == 2))

    def test_empty_signals(self):
        """
        Test the main function with empty signals.

        Verifies that the output signals remain empty.
        """
        input_data = {
            "signal": [
                [],
                [1, 2, 3],
                []
            ],
            "size": [0, 3, 0]
        }
        input_file = self.create_temp_feather_file(input_data)
        output_file = self.create_temp_feather_file({})

        main(input_file, output_file)

        df_output = pd.read_feather(output_file)
        self.assertTrue(
            all(len(signal) == 0 for signal in df_output['signal']))
        self.assertTrue(all(df_output['size'] == 0))

    def test_large_number_of_signals(self):
        """
        Test the main function with a large number of signals.

        Verifies that all signals are truncated to the shortest signal length.
        """
        num_signals = 1000
        max_length = 100
        signals = [list(np.random.rand(np.random.randint(1, max_length)))
                   for _ in range(num_signals)]
        input_data = {
            "signal": signals,
            "size": [len(signal) for signal in signals]
        }
        input_file = self.create_temp_feather_file(input_data)
        output_file = self.create_temp_feather_file({})

        main(input_file, output_file)

        df_output = pd.read_feather(output_file)
        min_length = min(len(signal) for signal in signals)
        self.assertTrue(
            all(len(signal) == min_length for signal in df_output['signal']))
        self.assertTrue(all(df_output['size'] == min_length))

    def test_error_handling_file_not_found(self):
        """
        Test the main function with a non-existent input file.

        Verifies that a FileNotFoundError is raised.
        """
        with self.assertRaises(FileNotFoundError):
            main("non_existent_file.feather", "output.feather")

    def test_error_handling_invalid_data(self):
        """
        Test the main function with invalid data in the input file.

        Verifies that a ValueError is raised.
        """
        input_data = {
            "signal": [
                "[1, 2, 3]",
                "invalid",
                "[4, 5, 6]"
            ],
            "size": [3, 1, 3]
        }
        input_file = self.create_temp_csv_file(input_data)
        output_file = self.create_temp_feather_file({})

        with self.assertRaises(ValueError):
            main(input_file, output_file)


if __name__ == '__main__':
    unittest.main()
