import struct
import bluepy
import logging

logger = logging.getLogger(__name__)

COMPLETE_LOCAL_NAME_TYPE_CODE = 0x09

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
        self.peripheral = bluepy.btle.Peripheral(scan_entry)
        self.service = self.peripheral.getServiceByUUID(self.SERVICE_UUID)
        self.characteristic = self.service.getCharacteristics(self.CHARACTERISTIC_UUID)[0]

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
        data = self.characteristic.read()
        try:
            ranges = struct.unpack('f'*(len(data)/4), data)
        except struct.error as exc:
            #logger.error(exc)
            raise exc
    
        return ranges