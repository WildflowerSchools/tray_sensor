from tray_sensor import scanner
from database_connection.csv import DatabaseConnectionCSV
import argparse
import logging
import time
import os

def main():
    parser = argparse.ArgumentParser(
        description='Read data from tray sensors and save to local CSV file.')
    parser.add_argument(
        '-d',
        '--dir',
        default = '.',
        help = 'path to directory for output file (default is .)'
    )
    parser.add_argument(
        '-o',
        '--output_file',
        default = 'tray_sensor_data',
        help = 'base of filename for output file; timestamp and .csv extension added automatically (default is tray_sensor_data)'
    )
    parser.add_argument(
        '-c',
        '--collection_period',
        type = int,
        default = 300,
        help = 'duration of data collection between scans for tags, in seconds (default is 300)'
    )
    parser.add_argument(
        '-t',
        '--timeout',
        type = int,
        default = 10,
        help = 'duration of scan for tags, in seconds (default 10)'
    )
    parser.add_argument(
        '-l',
        '--loglevel',
        help = 'log level (e.g., debug or warning or info)'
    )
    # Read arguments
    args = parser.parse_args()
    directory = args.dir
    filename_base = args.output_file
    collection_period = args.collection_period
    timeout = args.timeout
    loglevel = args.loglevel
    # Set log level
    if loglevel is not None:
        numeric_loglevel = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_loglevel, int):
            raise ValueError('Invalid log level: %s'.format(loglevel))
        logging.basicConfig(level=numeric_loglevel)
    # Construct path
    file_timestamp = time.strftime('%y%m%d_%H%M%S', time.gmtime())
    path = os.path.join(
        directory,
        '{}_{}.csv'.format(
            filename_base,
            file_timestamp))
    # Initialize database
    range_data_field_names = ['range_anchor{:02}'.format(anchor_index) for anchor_index in range(16)]
    convert_to_string_functions = {range_data_field_names[anchor_index]: lambda range: '{:.4f}'.format(range) for anchor_index in range(16)}
    convert_from_string_functions = {range_data_field_names[anchor_index]: lambda string: float(string) for anchor_index in range(16)}
    data_field_names = ['device_local_name'] + range_data_field_names
    database_connection = DatabaseConnectionCSV(
        path,
        data_field_names = data_field_names,
        convert_to_string_functions = convert_to_string_functions,
        convert_from_string_functions = convert_from_string_functions
    )
    # Scan for tags
    sc = scanner.Scanner(collection_period, timeout)
    sc.find_new_tags()
    # Collect data
    sc.run(database_connection)

if __name__ == "__main__":
    main()