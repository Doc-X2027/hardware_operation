"""Identity selection must never silently fall back to a webcam."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
from usb_camera_linux import device


class DeviceTests(unittest.TestCase):
    def test_missing_target_does_not_fall_back(self):
        with patch.object(device.sys, 'platform', 'linux'), patch.object(Path, 'glob', return_value=[]):
            with self.assertRaisesRegex(RuntimeError, '不会回退'):
                device.select_device()

    def test_identity_and_index_must_both_match(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usb = root / 'usb'
            usb.mkdir()
            for key, value in {'idVendor': '2993', 'idProduct': '0858', 'serial': '20240307110322'}.items():
                (usb / key).write_text(value)
            interface = usb / 'interface'
            interface.mkdir()
            node = root / 'video4'
            node.mkdir()
            (node / 'index').write_text('0')
            (node / 'name').write_text('icspring camera')
            (node / 'device').symlink_to(interface)
            with patch.object(device.sys, 'platform', 'linux'), patch.object(Path, 'glob', return_value=[node]):
                self.assertEqual(device.select_device()[0], '/dev/video4')
                with self.assertRaises(RuntimeError):
                    device.select_device(0)
                (usb / 'serial').write_text('wrong-camera')
                with self.assertRaises(RuntimeError):
                    device.select_device()

    def test_black_and_flat_frames_are_flagged(self):
        self.assertTrue(device.frame_stats(np.zeros((20, 20, 3), dtype=np.uint8))[0])
        self.assertTrue(device.frame_stats(np.full((20, 20, 3), 80, dtype=np.uint8))[0])
        gradient = np.tile(np.arange(100, dtype=np.uint8), (20, 1))
        self.assertFalse(device.frame_stats(gradient)[0])

    def test_windows_requires_explicit_index(self):
        with patch.object(device.sys, 'platform', 'win32'):
            with self.assertRaises(RuntimeError):
                device.select_device()
            self.assertEqual(device.select_device(1)[0], 1)
