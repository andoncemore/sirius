import unittest

from PIL import Image, ImageDraw

from sirius.coding import encoders
from sirius.protocol import messages

class EncodersCase(unittest.TestCase):
    # AddDeviceEncryptionKey
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

    # SetDeliveryAndPrint
    def test_set_delivery_and_print(self):
        command = messages.SetDeliveryAndPrint('some-device-address', self.bw_2x2())

        json = encoders.encode_bridge_command('some-bridge-address', command, 1, '0')

        expected_json = {
            'type': 'DeviceCommand',
            'bridge_address': 'some-bridge-address',
            'device_address': 'some-device-address',
            'command_id': 1,
            'timestamp': '0',
            'binary_payload': 'AQABAAEAAAAAAAAAJwAAACMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECAQ=='
        }

        self.assertDictEqual(expected_json, json)

    # SetDelivery
    def test_set_delivery(self):
        command = messages.SetDelivery('some-device-address', self.bw_2x2())

        json = encoders.encode_bridge_command('some-bridge-address', command, 1, '0')

        expected_json = {
            'type': 'DeviceCommand',
            'bridge_address': 'some-bridge-address',
            'device_address': 'some-device-address',
            'command_id': 1,
            'timestamp': '0',
            'binary_payload': 'AQACAAEAAAAAAAAAJwAAACMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECAQ=='
        }

        self.assertDictEqual(expected_json, json)

    # SetDeliveryAndPrintNoFace
    def test_set_delivery_and_print_no_face(self):
        command = messages.SetDeliveryAndPrintNoFace('some-device-address', self.bw_2x2())

        json = encoders.encode_bridge_command('some-bridge-address', command, 1, '0')

        expected_json = {
            'type': 'DeviceCommand',
            'bridge_address': 'some-bridge-address',
            'device_address': 'some-device-address',
            'command_id': 1,
            'timestamp': '0',
            'binary_payload': 'AQARAAEAAAAAAAAAJwAAACMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECAQ=='
        }

        self.assertDictEqual(expected_json, json)

    # SetDeliveryNoFace
    def test_set_delivery_no_face(self):
        command = messages.SetDeliveryNoFace('some-device-address', self.bw_2x2())

        json = encoders.encode_bridge_command('some-bridge-address', command, 1, '0')

        expected_json = {
            'type': 'DeviceCommand',
            'bridge_address': 'some-bridge-address',
            'device_address': 'some-device-address',
            'command_id': 1,
            'timestamp': '0',
            'binary_payload': 'AQASAAEAAAAAAAAAJwAAACMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECAQ=='
        }

        self.assertDictEqual(expected_json, json)

    # SetPersonality
    def test_set_personality(self):
        command = messages.SetPersonality('some-device-address', self.bw_2x2(), self.bw_2x2(), self.bw_2x2(), self.bw_2x2())

        json = encoders.encode_bridge_command('some-bridge-address', command, 1, '0')

        expected_json = {
            'type': 'DeviceCommand',
            'bridge_address': 'some-bridge-address',
            'device_address': 'some-device-address',
            'command_id': 1,
            'timestamp': '0',
            'binary_payload': 'AQACAQEAAAAAAAAAnAAAACMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECAQ=='
        }

        self.assertDictEqual(expected_json, json)

    # SetPersonalityWithMessage
    def test_set_personality_with_message(self):
        command = messages.SetPersonalityWithMessage('some-device-address', self.bw_2x2(), self.bw_2x2(), self.bw_2x2(), self.bw_2x2(), self.bw_2x2())

        json = encoders.encode_bridge_command('some-bridge-address', command, 1, '0')

        expected_json = {
            'type': 'DeviceCommand',
            'bridge_address': 'some-bridge-address',
            'device_address': 'some-device-address',
            'command_id': 1,
            'timestamp': '0',
            'binary_payload': 'AQABAQEAAAAAAAAAwwAAACMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECAQ=='
        }

        self.assertDictEqual(expected_json, json)

    # SetQuip
    def test_set_quip(self):
        command = messages.SetQuip('some-device-address', self.bw_2x2(), self.bw_2x2(), self.bw_2x2())

        json = encoders.encode_bridge_command('some-bridge-address', command, 1, '0')

        expected_json = {
            'type': 'DeviceCommand',
            'bridge_address': 'some-bridge-address',
            'device_address': 'some-device-address',
            'command_id': 1,
            'timestamp': '0',
            'binary_payload': 'AQACAgEAAAAAAAAAdQAAACMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECASMAAAAAABUAAAAdcwPoHWHQHS8PHUSAGyoAAAAAADABAwAAAAECAQ=='
        }

        self.assertDictEqual(expected_json, json)

    # Create 2x2 with white/black checkerboard:
    #
    #    01
    # 0  WB
    # 1  BW
    def bw_2x2(self):
        im = Image.new("1", (2, 2), 0)

        draw = ImageDraw.Draw(im)
        draw.point((0, 0), 1)
        draw.point((1, 1), 1)

        return im
