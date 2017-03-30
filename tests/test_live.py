import unittest
import sys
import os

try:
    from instagram_private_api_extensions import live
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api_extensions import live


class TestLive(unittest.TestCase):

    TEST_MPD_URL = 'http://127.0.01:8000/mpd/17875351285037717.mpd'

    def test_downloader(self):
        dl = live.Downloader(
            mpd=self.TEST_MPD_URL,
            output_dir='output',
            duplicate_etag_retry=2)
        dl.run()
        output_file = 'output.mp4'
        dl.stitch(output_file, cleartempfiles=False)
        self.assertTrue(os.path.isfile(output_file), '%s not generated' % output_file)


if __name__ == '__main__':
    unittest.main()
