from tray_sensor import scanner
from database_connection_honeycomb import DatabaseConnectionHoneycomb
import argparse
import logging
import time
import os

def main():
    parser = argparse.ArgumentParser(
        description='Read data from tray sensors and save to Honeycomb.')
    parser.add_argument(
        '-e',
        '--env_name',
        default = 'wework-3a',
        help = 'Honeycomb environment name (default is wework-3a)'
    )
    parser.add_argument(
        '-t',
        '--type',
        default = 'DEVICE',
        help = 'Honeycomb object type (default is DEVICE)'
    )
    parser.add_argument(
        '-i',
        '--id_field_name',
        default = 'part_number',
        help = 'name of Honeycomb field in which to store object ID (default is part_number)'
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
    environment_name_honeycomb = args.env_name
    object_type_honeycomb = args.type
    object_id_field_name_honeycomb = args.id_field_name
    collection_period = args.collection_period
    timeout = args.timeout
    loglevel = args.loglevel
    # Set log level
    if loglevel is not None:
        numeric_loglevel = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_loglevel, int):
            raise ValueError('Invalid log level: %s'.format(loglevel))
        logging.basicConfig(level=numeric_loglevel)
    # Initialize database
    database_connection = DatabaseConnectionHoneycomb(
        environment_name_honeycomb = environment_name_honeycomb,
        object_type_honeycomb = object_type_honeycomb,
        object_id_field_name_honeycomb = object_id_field_name_honeycomb
    )
    # Scan for tags
    sc = scanner.Scanner(collection_period, timeout)
    sc.find_new_tags()
    # Collect data
    sc.run(database_connection)

if __name__ == "__main__":
    main()
