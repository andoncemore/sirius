from PIL import Image, ImageDraw
import unittest

from sirius.coding import image_encoding

class ImageCase(unittest.TestCase):
    def test_normal_text(self):
        data = image_encoding.html_to_png(
            '<html><body style="margin: 0px; height: 10px;"></body></html>'
            )
        image = Image.open(data)
        self.assertEquals(image.size[0], 384)
        self.assertEquals(image.size[1], 10)

    def test_normal_height(self):
        data = image_encoding.html_to_png(
            '<html><body style="margin: 0px; height: 100px;"></body></html>'
            )
        image = Image.open(data)
        self.assertEquals(image.size[0], 384)
        self.assertEquals(image.size[1], 100)


class PipeTestCase(unittest.TestCase):
    def test_specific_image_rle(self):
        image = Image.new('1', (3, 3), 0)

        # 3x3 checkerboard
        draw = ImageDraw.Draw(image)
        draw.point((0, 0), 1)
        draw.point((2, 0), 1)
        draw.point((1, 1), 1)
        draw.point((0, 2), 1)
        draw.point((2, 2), 1)

        n_bytes, rle = image_encoding.rle_from_bw(image)
        self.assertEqual(rle, b'\x01\x09\x00\x00\x00\x01\x01\x01\x01\x01\x01\x01\x01\x01')
        self.assertEquals(n_bytes, 9)

    def test_full(self):
        data = image_encoding.html_to_png(
            '<html><body style="margin: 0px; height: 10px;"></body></html>'
            )

        image = Image.open(data)
        image = image_encoding.crop_384(image)
        image = image_encoding.convert_to_1bit(image)

        n_bytes, _ = image_encoding.rle_from_bw(image)
        self.assertEquals(n_bytes, 3840)

    def test_default_pipeline(self):
        n_bytes, _ = image_encoding.rle_from_bw(
            image_encoding.default_pipeline(
            '<html><body style="margin: 0px; height: 10px;"></body></html>'
            )
        )
        self.assertEquals(n_bytes, 3840)
