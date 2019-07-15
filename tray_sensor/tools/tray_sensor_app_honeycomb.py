from tray_sensor import scanner
from database_connection_honeycomb import DatabaseConnectionHoneycomb
import argparse
import logging
import time
import os

def main():
    parser = argparse.ArgumentParser(
        description='Read data from tray sensors and save to Honeycomb.',
        epilog = 'Anchor ID file should be a simple text file, one anchor ID per line. If anchor IDs are not specified, tool will use anchor_00 through anchor_15 (assuming 16 values per reading).'
    )
    parser.add_argument(
        '-e',
        '--env_name',
        help = 'Honeycomb environment name'
    )
    parser.add_argument(
        '-o',
        '--object_type',
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
        '-a',
        '--anchor_id_file',
        help = 'path to file containing anchor IDs'
    )
    parser.add_argument(
        '-l',
        '--loglevel',
        help = 'log level (e.g., debug or warning or info)'
    )
    # Read arguments
    args = parser.parse_args()
    environment_name_honeycomb = args.env_name
    object_type_honeycomb = args.object_type
    object_id_field_name_honeycomb = args.id_field_name
    collection_period = args.collection_period
    timeout = args.timeout
    anchor_id_file = args.anchor_id_file
    loglevel = args.loglevel
    # Check for Honeycomb environment
    if environment_name_honeycomb is None:
        raise ValueError('Honeycomb environment must be specified')
    # Set log level
    if loglevel is not None:
        numeric_loglevel = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_loglevel, int):
            raise ValueError('Invalid log level: %s'.format(loglevel))
        logging.basicConfig(level=numeric_loglevel)
    # Construct anchor ID list
    if anchor_id_file is None:
        anchor_ids  =  None
    else:
        anchor_ids = []
        with open(anchor_id_file, mode = 'r') as fh:
            for line in fh:
                anchor_ids.append(line.rstrip())
    print('Anchor IDs: {}'.format(anchor_ids))
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
    sc.run(database_connection, anchor_ids)

if __name__ == "__main__":
    main()
