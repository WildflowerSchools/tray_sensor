from tray_sensor import scanner
from tray_sensor.databases.measurement_database.csv_local import MeasurementDatabaseCSVLocal

def main():
    directory = 'output'
    filename_base = 'tray_sensor_data'
    fields = ['timestamp', 'mac_address', 'ranging_data']
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
