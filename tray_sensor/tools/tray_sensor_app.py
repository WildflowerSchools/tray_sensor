from tray_sensor import scanner
from tray_sensor.databases.measurement_database.csv_local import MeasurementDatabaseCSVLocal
import argparse

TRAY_SENSOR_DATA_FIELDS = ['timestamp', 'mac_address', 'ranging_data']

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
    measurement_database = MeasurementDatabaseCSVLocal(
        directory = directory,
        filename_base = filename_base,
        fields = fields
    )
    sc = scanner.Scanner()
    sc.find_new_tags()
    print(sc.tags)
    sc.run(measurement_database)

if __name__ == "__main__":
    main()
