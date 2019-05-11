import bluepy.btle
from collections import defaultdict
from .tag import TagDevice
import logging
import time
import datetime


logger = logging.getLogger(__name__)

DEFAULT_SCAN_PERIOD=10

COMPLETE_16B_SERVICES_TYPE_CODE = 0x03
COMPLETE_16B_SERVICES_VALUE = '00001811-0000-1000-8000-00805f9b34fb'


def find_tray_sensors(timeout=1):
    # find tray sensors by complete 16b services value
    scanner = bluepy.btle.Scanner()
    tray_sensor_scan_entries = []
    scan_entries = scanner.scan(timeout)
    for scan_entry in scan_entries:
        scan_data = scan_entry.getScanData()
        for type_code, description, value in scan_data:
            if (type_code == COMPLETE_16B_SERVICES_TYPE_CODE and
                value == COMPLETE_16B_SERVICES_VALUE):
                tray_sensor_scan_entries.append(scan_entry)
    return tray_sensor_scan_entries

class Scanner:
    def __init__(self, scan_period=DEFAULT_SCAN_PERIOD):
        self.tags = {}
        self.scan_period = scan_period

    def find_new_tags(self):
        tag_scan_entries = find_tray_sensors()
        for tag_scan_entry in tag_scan_entries:
            mac_address = tag_scan_entry.addr
            if mac_address not in self.tags:
                try:
                    tag = TagDevice(tag_scan_entry)
                    self.tags[mac_address] = tag
                except bluepy.btle.BTLEDisconnectError as exc:
                    pass
        logger.debug('Found tags: {}'.format(', '.join(['{} ({})'.format(tag.name, mac_address) for mac_address, tag in self.tags.items()])))

    def run(self, measurement_database):
        data = defaultdict(list)
        time_0 = time.time()
        while True:
            bad_tags = []
            for tag_mac_address, tag in self.tags.items():
                try:
                    reading = tag.read()
                except Exception as exc:
                    logger.info("Error reading from {} ({})".format(tag.name, tag_mac_address))
                    bad_tags.append(tag_mac_address)
                    tag.close()
                else:
                    logger.debug("{} :: {}".format(tag_mac_address, [None if x is None else "{:.3f}".format(x) for x in reading]))
                    data[tag_mac_address] = reading
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
                    device_data = {
                        'timestamp': timestamp,
                        'mac_address': tag_mac_address,
                        'local_name': tag.name,
                        'ranging_data': reading
                    }
                    measurement_database.put_device_data(device_data)

            # remove bad tags
            self.tags = {key: value for key, value in self.tags.items() if key not in bad_tags}

            # if scan period elapses, find new tags
            time_1 = time.time()
            elapsed_time  = time_1 - time_0
            if elapsed_time >= self.scan_period:
                time_0 = time_1
                self.find_new_tags()
