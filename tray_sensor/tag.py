import struct
import bluepy
import tenacity
import logging

logger = logging.getLogger(__name__)

COMPLETE_LOCAL_NAME_TYPE_CODE = 0x09

NUM_ANCHORS = 16
NUM_BYTES_PER_ANCHOR = 4

SENTINEL_VALUE_BYTES = b'\xd1\xaa\xaa\xba'
SENTINEL_VALUE_FLOAT = struct.unpack('f', SENTINEL_VALUE_BYTES)[0]

RETRY_INITIAL_WAIT = 0.1 # seconds
RETRY_NUM_ATTEMPTS = 4

exponential_retry = tenacity.retry(
        stop = tenacity.stop_after_attempt(RETRY_NUM_ATTEMPTS),
        wait = tenacity.wait_exponential(multiplier=RETRY_INITIAL_WAIT/2),
        before = tenacity.before_log(logger, logging.DEBUG),
        after = tenacity.after_log(logger, logging.DEBUG),
        before_sleep = tenacity.before_sleep_log(logger, logging.WARNING))

def get_name(scan_entry):
    scan_data = scan_entry.getScanData()
    for type_code, description, value in scan_data:
        if type_code == COMPLETE_LOCAL_NAME_TYPE_CODE:
            return value
    raise IOError("Unable to read device local name for {}".format(scan_entry))

class TagDevice:
    SERVICE_UUID = "59462F12-9543-9999-12C8-58B459A2712D"
    CHARACTERISTIC_UUID = "5C3A659E-897E-45E1-B016-007107C96DF7"

    def __init__(self, scan_entry):
        self.scan_entry = scan_entry
        self._name = get_name(self.scan_entry)
        self.peripheral = self._get_peripheral()
        self.service = self._get_service()
        self.characteristic = self._get_characteristic()

    def close(self):
        try:
            self.peripheral.disconnect()
        except:
            pass

    @property
    def name(self):
        return self._name

    @property
    def mac_address(self):
        return self.scan_entry.addr

    def read(self):
        ## '0x78 0x8A 0x93 0x40 0x14 0x1B 0x83 0x40 0x62 0x81 0x82 0x40 0xCF 0xA7 0x82 0x40 0x26 0x3D 0x90 0x40 0xAD 0x3C 0x8D 0x40 0x51 0xD7 0x93 0x40 0x0C 0x64 0x93 0x40 0xA8 0x5E 0x42 0x40 0x26 0x6B 0x40 0x40 0x60 0x7C 0x5C 0x40 0x46 0xC8 0x56 0x40 0xCD 0xC7 0x53 0x40 0xB9 0x1F 0x49 0x40 0x16 0xFD 0x60 0x40 0xAB 0x4E 0x7F 0x40'
        ## 'x\x8a\x93@\x14\x1b\x83@b\x81\x82@\xcf\xa7\x82@&=\x90@\xad<\x8d@Q\xd7\x93@\x0cd\x93@\xa8^B@&k@@`|\\@F\xc8V@\xcd\xc7S@\xb9\x1fI@\x16\xfd`@\xabN\x7f@'
        data = self._read_characteristic()
        if len(data) != NUM_ANCHORS * NUM_BYTES_PER_ANCHOR:
            raise ValueError('Expected {} bytes for {} anchors but received {} bytes'.format(
                NUM_ANCHORS * NUM_BYTES_PER_ANCHOR,
                NUM_ANCHORS,
                len(data)
            ))
        try:
            ranges = struct.unpack('f'*NUM_ANCHORS, data)
        except struct.error as exc:
            #logger.error(exc)
            raise exc
        # Remove missing values
        ranges = [None if range == SENTINEL_VALUE_FLOAT else range for range in ranges]
        return ranges

    @exponential_retry
    def _get_peripheral(self):
        peripheral = bluepy.btle.Peripheral(self.scan_entry)
        return peripheral

    def _get_service(self):
        try:
            service = self.peripheral.getServiceByUUID(self.SERVICE_UUID)
        except Exception as exc:
            logger.warning('Failed to retrieve service for {} ({}) [Exception: {}]. Attempting to reconnect.'.format(
                self.name,
                self.mac_address,
                exc))
            self.close()
            self.peripheral = self._get_peripheral()
            service = self.peripheral.getServiceByUUID(self.SERVICE_UUID)
        return service

    def _get_characteristic(self):
        try:
            characteristic = self.service.getCharacteristics(self.CHARACTERISTIC_UUID)[0]
        except Exception as exc:
            logger.warning('Failed to retrieve characteristic from {} ({}) [Exception: {}]. Attempting to reconnect.'.format(
                self.name,
                self.mac_address,
                exc))
            self.close()
            self.peripheral = self._get_peripheral()
            self.service = self._get_service()
            characteristic = self.service.getCharacteristics(self.CHARACTERISTIC_UUID)[0]
        return characteristic

    def _read_characteristic(self):
        try:
            data = self.characteristic.read()
        except Exception as exc:
            logger.warning('Failed to read data from {} ({}) [Exception: {}]. Attempting to reconnect.'.format(
                self.name,
                self.scan_entry.addr,
                exc))
            self.close()
            self.peripheral = self._get_peripheral()
            self.service = self._get_service()
            self.characteristic = self._get_characteristic()
            data = self.characteristic.read()
        return data
