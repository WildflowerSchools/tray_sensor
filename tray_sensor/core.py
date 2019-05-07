"""
Provide core classes, methods, and functions for communicating with Wildflower tray sensors devices via BLE.
"""
import bluepy.btle
# import bitstruct
# import tenacity
import logging
# import time
# import warnings
import datetime

logger = logging.getLogger(__name__)

# retry_initial_wait = 0.1 # seconds
# retry_num_attempts = 4
# exponential_retry = tenacity.retry(
#         stop = tenacity.stop_after_attempt(retry_num_attempts),
#         wait = tenacity.wait_exponential(multiplier=retry_initial_wait/2),
#         before = tenacity.before_log(logger, logging.DEBUG),
#         after = tenacity.after_log(logger, logging.DEBUG),
#         before_sleep = tenacity.before_sleep_log(logger, logging.WARNING))

RANGING_SERVICE_UUID = '59462F12-9543-9999-12C8-58B459A2712D'
RANGING_CHARACTERISTIC_UUID = '5C3A659E-897E-45E1-B016-007107C96DF7'

# BLE advertising data codes
COMPLETE_16B_SERVICES_TYPE_CODE = int('0x03', 16)
COMPLETE_16B_SERVICES_VALUE = '00001811-0000-1000-8000-00805f9b34fb'
COMPLETE_LOCAL_NAME_TYPE_CODE = int('0x09', 16)

def find_tray_sensor_devices(timeout = 10):
    scanner = bluepy.btle.Scanner()
    tray_sensor_devices = {}
    scan_entries = scanner.scan(timeout)
    for scan_entry in scan_entries:
        scan_data = scan_entry.getScanData()
        for type_code, description, value in scan_data:
            if (type_code == COMPLETE_16B_SERVICES_TYPE_CODE and
                value == COMPLETE_16B_SERVICES_VALUE):
                mac_address = scan_entry.addr
                tray_sensor_device = TraySensorBLE(scan_entry)
                tray_sensor_devices[mac_address] = tray_sensor_device
    return tray_sensor_devices

class TraySensorBLE:
    """
    Class to represent the BLE interface to a tray sensor.

    Attributes:
        mac_address (str): MAC address as colon-separated hex string
    """
    def __init__(self, scan_entry):
        self._scan_entry = scan_entry
        # self._peripheral = None
        # self._network_node_service = None
        self.mac_address = scan_entry.addr
        self.local_name = None
        scan_data = scan_entry.getScanData()
        for type_code, description, value in scan_data:
            if type_code == COMPLETE_LOCAL_NAME_TYPE_CODE:
                self.local_name = value

    def read_ranging_data(self):
        peripheral = bluepy.btle.Peripheral(self._scan_entry)
        ranging_service = peripheral.getServiceByUUID(RANGING_SERVICE_UUID)
        characteristic = ranging_service.getCharacteristics(RANGING_CHARACTERISTIC_UUID)[0]
        bytes = characteristic.read()
        return len(bytes)

def collect_data(
    measurement_database,
    mac_addresses,
    cycles = 1,
    timeout = 10):
    """
    Collect specified data from specified devices and save in specified
    database.

    If the number of cycles is set to zero, data will be collected until a
    keyboard interrupt.

    Parameters:
        measurement_database (MeasurementDatabase): Database where data should be stored
        mac_addresses (list): MAC addresses for devices we want to collect from
        cycles (int): Number of times to collect data from each device (default is 1)
    """
    if cycles == 0:
        logger.info('Collecting data until keyboard interrupt is detected'.format(cycles))
    else:
        logger.info('Collecting data for {} cycles'.format(cycles))
    cycles_completed = 0
    scanner = bluepy.btle.Scanner().withDelegate(ShoeSensorDelegate(measurement_database, mac_addresses))
    try:
        while cycles == 0 or cycles_completed < cycles:
            logger.info('Data collection cycle {}'.format(cycles_completed + 1))
            scanner.scan(timeout)
            cycles_completed += 1
    except KeyboardInterrupt:
        logger.warning('Keyboard interrupt detected. Shutting down data collection.')

class ShoeSensorDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self, measurement_database, mac_addresses):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.mac_addresses = mac_addresses
        self.measurement_database = measurement_database

    def handleDiscovery(self, dev, isNewDev, isNewData):
        mac_address = dev.addr
        if mac_address in self.mac_addresses:
            timestamp = datetime.datetime.now(datetime.timezone.utc)
            rssi = dev.rssi
            logger.debug('{}: {} dB'.format(mac_address, rssi))
            device_data = {
                'timestamp': timestamp,
                'mac_address': mac_address,
                'rssi': rssi
            }
            self.measurement_database.put_device_data(device_data)
