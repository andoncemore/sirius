# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot
from snapshottest.file import FileSnapshot


snapshots = Snapshot()

snapshots['ImageSnapshotCase::test_snapshot_fixtures hello_world'] = FileSnapshot('snap_test_image_coding/ImageSnapshotCase::test_snapshot_fixtures hello_world.png')
