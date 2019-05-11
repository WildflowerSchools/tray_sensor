from tray_sensor import scanner
from tray_sensor.databases.measurement_database.csv_local import MeasurementDatabaseCSVLocal
import argparse
import logging

TRAY_SENSOR_DATA_FIELDS = [
    'timestamp',
    'mac_address',
    'local_name',
    'ranging_data'
]

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
        '-l',
        '--loglevel',
        help = 'log level (e.g., debug or warning or info)'
    )
    # Read arguments
    args = parser.parse_args()
    directory = args.dir
    filename_base = args.output_file
    loglevel = args.loglevel
    fields = TRAY_SENSOR_DATA_FIELDS
    # Set log level
    if loglevel is not None:
        numeric_loglevel = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_loglevel, int):
            raise ValueError('Invalid log level: %s'.format(loglevel))
        logging.basicConfig(level=numeric_loglevel)
    # Initialize database
    measurement_database = MeasurementDatabaseCSVLocal(
        directory = directory,
        filename_base = filename_base,
        fields = fields
    )
    # Scan for tags
    sc = scanner.Scanner()
    sc.find_new_tags()
    logging.info('Found tags: {}'.format(', '.join(['{} ({})'.format(tag.name, mac_address) for mac_address, tag in sc.tags.items()])))
    # Collect data
    sc.run(measurement_database)

if __name__ == "__main__":
    main()
