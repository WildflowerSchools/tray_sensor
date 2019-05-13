"""
Define constants that are shared by the submodules of tray_sensor
"""

import collections

# Information about data fields across interfaces
DATA_FIELD_INFO = collections.OrderedDict([
    ('timestamp', {
        'field_name_sentence_caps': "Timestamp",
        'type': 'datetime',
        'string_format': '{}'
    }),
    ('mac_address', {
        'field_name_sentence_caps': "MAC address",
        'type': 'string',
        'string_format': '{}',
    }),
    ('local_name', {
        'field_name_sentence_caps': "Local name",
        'type': 'string',
        'string_format': '{}',
    }),
    ('ranging_data', {
        'field_name_sentence_caps': "Ranging data",
        'type': 'float',
        'list': True,
        'max_list_length': 16,
        'string_format': '{:.4}',
    }),
    ('rssi', {
        'field_name_sentence_caps': "RSSI",
        'type': 'integer',
        'string_format': '{}',
    })])
