import unittest

from sirius.coding import encoders
from sirius.protocol import messages




class CodingCase(unittest.TestCase):
    def test_add_device_encryption_key(self):
        claim_code = '6xwh-441j-8115-zyrh'
        expected_encryption_key = 'F7D9bmztHV32+WJScGZR0g=='

        command = messages.AddDeviceEncryptionKey(
            'some-bridge-address',
            'some-device-address',
            claim_code
        )

        json = encoders.encode_bridge_command('some-bridge-address', command, 1, '0')

        expected_json = {
            'type': 'BridgeCommand',
            'bridge_address': 'some-bridge-address',
            'command_id': 1,
            'timestamp': '0',
            'json_payload': {
                'name': 'add_device_encryption_key',
                'params': {
                    'device_address': 'some-device-address',
                    'encryption_key': expected_encryption_key,
                }
            }
        }

        self.assertDictEqual(expected_json, json)

