import bluepy.btle
from collections import defaultdict
from .tag import TagDevice
import logging
import time
import datetime


logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_PERIOD = 300
DEFAULT_TIMEOUT = 10

COMPLETE_16B_SERVICES_TYPE_CODE = 0x03
COMPLETE_16B_SERVICES_VALUE = '00001811-0000-1000-8000-00805f9b34fb'


def find_tray_sensors(timeout = DEFAULT_TIMEOUT):
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
    def __init__(self, collection_period = DEFAULT_COLLECTION_PERIOD, timeout = DEFAULT_TIMEOUT):
        self.tags = {}
        self.collection_period = collection_period
        self.timeout = timeout

    def find_new_tags(self):
        logger.info('Scanning for new tags for {} seconds'.format(self.timeout))
        # Scan for tray sensors
        tag_scan_entries = find_tray_sensors(self.timeout)
        # Add new tray sensors to our list
        for tag_scan_entry in tag_scan_entries:
            mac_address = tag_scan_entry.addr
            if mac_address not in self.tags:
                try:
                    tag = TagDevice(tag_scan_entry)
                    self.tags[mac_address] = tag
                    logger.info('Found tag: {} ({})'.format(tag.name, mac_address))
                except Exception as exc:
                    logger.warning("Failed to connect to {} [Exception: {}]. Not adding to tag list.".format(mac_address, exc))

    def clear_tags(self):
        logger.info('Clearing tag list')
        # Close connections
        for mac_address, tag in self.tags.items():
            tag.close()
        # Clear tag list
        self.tags = {}

    def reset_tags(self):
        self.clear_tags()
        self.find_new_tags()

    def run(self, database_connection, anchor_ids):
        logger.info('Collecting data')
        data = defaultdict(list)
        time_0 = time.time()
        logger.info('Collecting data for {} seconds'.format(self.collection_period))
        while True:
            bad_tags = []
            for tag_mac_address, tag in self.tags.items():
                try:
                    reading = tag.read()
                except Exception as exc:
                    logger.warning("Error reading from {} ({}) [Exception: {}]. Removing from tag list.".format(tag.name, tag_mac_address, exc))
                    bad_tags.append(tag_mac_address)
                    tag.close()
                else:
                    logger.debug("{} :: {}".format(tag_mac_address, [None if x is None else "{:.3f}".format(x) for x in reading]))
                    data[tag_mac_address] = reading
                    timestamp = datetime.datetime.now(datetime.timezone.utc)
                    if anchor_ids is not None:
                        if len(anchor_ids) != len(reading):
                            raise ValueError('{} anchor IDs specified but device returned range data from {} anchors'.format(
                                len(anchor_ids),
                                len(reading)
                            ))
                    else:
                        anchor_ids = ['anchor_{:02}'.format(anchor_index) for anchor_index in range(len(reading))]
                    for anchor_index in range(len(reading)):
                        if reading[anchor_index] is not None:
                            device_data = {
                                'device_local_name': tag.name,
                                'anchor_id': anchor_ids[anchor_index],
                                'range': reading[anchor_index]
                            }
                            database_connection.write_data_object_time_series(
                                timestamp = timestamp,
                                object_id = tag_mac_address,
                                data = device_data
                            )

            # remove bad tags
            self.tags = {key: value for key, value in self.tags.items() if key not in bad_tags}

            # if collection period elapses, find new tags
            time_1 = time.time()
            elapsed_time  = time_1 - time_0
            if elapsed_time >= self.collection_period:
                self.reset_tags()
                time_0 = time.time()
                logger.info('Collecting data for {} seconds'.format(self.collection_period))
