import unittest
import sys
import os
import shutil

import responses
from requests.exceptions import ConnectionError

try:
    from instagram_private_api_extensions import live
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api_extensions import live


class TestLive(unittest.TestCase):
    """Tests for live related functions."""

    TEST_MPD_URL = 'http://127.0.01:8000/mpd/17875351285037717.mpd'

    @classmethod
    def setUpClass(cls):
        for f in ('output.mp4', 'output_singlethreaded.mp4',
                  'output_httperrors.mp4', 'output_404.mp4', 'output_connerror.mp4',
                  'output_respheaders.mp4', 'output_fragment_connerror.mp4'):
            if os.path.isfile(f):
                os.remove(f)
        for fd in ('output', 'output_singlethreaded', 'output_httperrors', 'output_404',
                   'output_connerror', 'output_respheaders', 'output_fragment_connerror'):
            if os.path.exists(fd):
                shutil.rmtree(fd, ignore_errors=True)

    def test_downloader(self):
        def check_status():
            return True

        dl = live.Downloader(
            mpd=self.TEST_MPD_URL,
            output_dir='output',
            duplicate_etag_retry=10,
            callback_check=check_status)
        dl.run()
        output_file = 'output.mp4'
        dl.stitch(output_file, cleartempfiles=False)
        self.assertTrue(os.path.isfile(output_file), '{0!s} not generated'.format(output_file))

    def test_downloader_404(self):
        def check_status():
            return True

        dl = live.Downloader(
            mpd=self.TEST_MPD_URL + 'x',
            output_dir='output_404',
            max_connection_error_retry=2,
            callback_check=check_status)
        dl.run()
        output_file = 'output_404.mp4'
        with self.assertRaises(Exception):
            dl.stitch(output_file, cleartempfiles=False)
        self.assertFalse(os.path.isfile(output_file), '{0!s} is generated'.format(output_file))

    def test_downloader_single_threaded(self):
        dl = live.Downloader(
            mpd=self.TEST_MPD_URL,
            output_dir='output_singlethreaded',
            duplicate_etag_retry=10,
            singlethreaded=True)
        dl.run()
        output_file = 'output_singlethreaded.mp4'
        dl.stitch(output_file, cleartempfiles=True)
        self.assertTrue(os.path.isfile(output_file), '{0!s} not generated'.format(output_file))

    @responses.activate
    def test_downloader_http_errors(self):
        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.GET, self.TEST_MPD_URL, status=500)
            rsps.add(responses.GET, self.TEST_MPD_URL, status=404)

            dl = live.Downloader(
                mpd=self.TEST_MPD_URL,
                output_dir='output_httperrors',
                duplicate_etag_retry=2,
                singlethreaded=True)
            dl.run()
            dl.stream_id = '17875351285037717'
            output_file = 'output_httperrors.mp4'
            dl.stitch(output_file, cleartempfiles=True)
            self.assertFalse(os.path.isfile(output_file), '{0!s} is generated'.format(output_file))

    @responses.activate
    def test_downloader_conn_error(self):
        exception = ConnectionError()
        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            max_retry = 3
            for _ in range(max_retry + 1):
                rsps.add(responses.GET, self.TEST_MPD_URL, body=exception)

            dl = live.Downloader(
                mpd=self.TEST_MPD_URL,
                output_dir='output_connerror',
                duplicate_etag_retry=2,
                singlethreaded=True,
                max_connection_error_retry=max_retry)
            dl.run()
            dl.stream_id = '17875351285037717'
            output_file = 'output_connerror.mp4'
            dl.stitch(output_file, cleartempfiles=True)
            self.assertFalse(os.path.isfile(output_file), '{0!s} not generated'.format(output_file))

    @responses.activate
    def test_downloader_fragment_dl_error(self):
        exception = ConnectionError()
        fragments = [
            'dash-hd1/17875351285037717-init.m4v',
            'dash-hd1/17875351285037717-281033.m4v',
            'dash-hd1/17875351285037717-282033.m4v',
            'dash-hd1/17875351285037717-283033.m4v',
            'dash-hd1/17875351285037717-284033.m4v',
            'dash-hd1/17875351285037717-285033.m4v',
            'dash-hd1/17875351285037717-286033.m4v',
            'dash-hd1/17875351285037717-287033.m4v',
            'dash-hd1/17875351285037717-288033.m4v',
            'dash-hd1/17875351285037717-289033.m4v',
            'dash-hd1/17875351285037717-290033.m4v',
            'dash-ld/17875351285037717-init.m4a',
            'dash-ld/17875351285037717-281033.m4a',
            'dash-ld/17875351285037717-282033.m4a',
            'dash-ld/17875351285037717-283033.m4a',
            'dash-ld/17875351285037717-284033.m4a',
            'dash-ld/17875351285037717-285033.m4a',
            'dash-ld/17875351285037717-286033.m4a',
            'dash-ld/17875351285037717-287033.m4a',
            'dash-ld/17875351285037717-288033.m4a',
            'dash-ld/17875351285037717-289033.m4a',
            'dash-ld/17875351285037717-290033.m4a',
        ]
        with open('mpdstub/mpd/17875351285037717.mpd', 'r') as f:
            mpd_content = f.read()
        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.GET, self.TEST_MPD_URL, body=mpd_content)
            max_retry = 1

            for fragment in fragments:
                for _ in range(max_retry + 1):
                    rsps.add(responses.GET, 'http://127.0.01:8000/' + fragment, body=exception)

            dl = live.Downloader(
                mpd=self.TEST_MPD_URL,
                output_dir='output_fragment_connerror',
                duplicate_etag_retry=2,
                singlethreaded=True,
                max_connection_error_retry=max_retry)
            dl.run()
            dl.stream_id = '17875351285037717'
            output_file = 'output_fragment_connerror.mp4'
            dl.stitch(output_file, cleartempfiles=True)
            self.assertFalse(os.path.isfile(output_file), '{0!s} not generated'.format(output_file))

    @responses.activate
    def test_downloader_resp_headers(self):
        with open('mpdstub/mpd/17875351285037717.mpd', 'r') as f:
            mpd_content = f.read()
            with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
                rsps.add(responses.GET, self.TEST_MPD_URL, body=mpd_content)
                rsps.add(responses.GET, self.TEST_MPD_URL, body=mpd_content,
                         adding_headers={'Cache-Control': 'max-age=1'})
                rsps.add(responses.GET, self.TEST_MPD_URL, body=mpd_content,
                         adding_headers={'X-FB-Video-Broadcast-Ended': '1'})

                dl = live.Downloader(
                    mpd=self.TEST_MPD_URL,
                    output_dir='output_respheaders')
                dl.run()

            with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
                rsps.add(responses.GET, self.TEST_MPD_URL, body=mpd_content,
                         adding_headers={'Cache-Control': 'max-age=1'})
                rsps.add(responses.GET, self.TEST_MPD_URL, body=mpd_content,
                         adding_headers={'Cache-Control': 'max-age=1000'})

                dl = live.Downloader(
                    mpd=self.TEST_MPD_URL,
                    output_dir='output_respheaders')
                dl.run()

            # Can't stitch and check for output because responses does not support
            # url pass through, so the segments cannot be downloaded.


if __name__ == '__main__':
    unittest.main()
