import os
from tempfile import TemporaryDirectory
from PIL import Image

import snapshottest
from snapshottest.file import FileSnapshot

from sirius.coding import image_encoding
from sirius.coding import templating


class ImageCodingSnapshotCase(snapshottest.TestCase):
    def _check_html(self, name, html):
        print('Cheking fixture named: %s' % name)

        with TemporaryDirectory() as tmpdir:
            data = image_encoding.html_to_png(html)
            image = Image.open(data)

            temp_file_name = os.path.join(tmpdir, '%s.png' % name)
            image.save(temp_file_name, format='PNG')
            self.assertMatchSnapshot(FileSnapshot(temp_file_name), name)

    def test_snapshot_fixtures(self):
        fixtures = {
            'hello_world': '<html><body>Hello, world!</body></html>',
        }

        for name, html in fixtures.items():
            self._check_html(name, html)

    def test_snapshot_template_fixtures(self):
        fixtures = {
            'hello_world': '<p>Hello, world!</p>',
        }

        for name, snippet in fixtures.items():
            self._check_html(name, templating.default_template(snippet, 'anonymous'))