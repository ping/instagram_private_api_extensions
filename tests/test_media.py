import unittest
import sys
import os
import time

try:
    from instagram_private_api_extensions import media
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api_extensions import media


class TestMedia(unittest.TestCase):

    TEST_IMAGE_PATH = 'media/test.jpg'
    TEST_IMAGE_SIZE = (640, 493)
    TEST_VIDEO_PATH = 'media/test.mp4'
    TEST_VIDEO_SIZE = (640, 360)
    TEST_VIDEO_DURATION = 60.0

    def test_prepare_image(self):
        _, size = media.prepare_image(
            self.TEST_IMAGE_PATH, max_size=(400, 400), aspect_ratios=0.8)
        self.assertLessEqual(size[0], 400, 'Invalid width.')
        self.assertLessEqual(size[1], 400, 'Invalid height.')
        self.assertEqual(round(1.0 * size[0] / size[1], 2), 0.8, 'Invalid aspect ratio.')

    def test_prepare_image2(self):
        _, size = media.prepare_image(
            self.TEST_IMAGE_PATH, max_size=(400, 350), aspect_ratios=(0.8, 1.2))
        self.assertLessEqual(size[0], 400, 'Invalid width.')
        self.assertLessEqual(size[1], 350, 'Invalid height.')
        ar = 1.0 * size[0] / size[1]
        self.assertLessEqual(round(ar, 2), 1.2)
        self.assertGreaterEqual(round(ar, 2), 0.8)

    def test_prepare_video(self):
        _, size, duration, _ = media.prepare_video(
            self.TEST_VIDEO_PATH, aspect_ratios=1.0, max_duration=10, save_path='media/output.mp4')
        self.assertEqual(duration, 10.0, 'Invalid duration.')
        self.assertEqual(size[0], size[1], 'Invalid width/length.')
        self.assertTrue(os.path.isfile('media/output.mp4'), 'Output file not generated.')

    def test_prepare_video2(self):
        _, size, duration, _ = media.prepare_video(
            self.TEST_VIDEO_PATH, max_size=(480, 480))
        self.assertEqual(duration, self.TEST_VIDEO_DURATION, 'Duration changed.')
        self.assertLessEqual(size[0], 480, 'Invalid width.')
        self.assertLessEqual(size[1], 480, 'Invalid height.')
        self.assertEqual(
            1.0 * size[0] / size[1],
            1.0 * self.TEST_VIDEO_SIZE[0] / self.TEST_VIDEO_SIZE[1],
            'Aspect ratio changed.')

    def test_prepare_video3(self):
        _, size, duration, _ = media.prepare_video(
            self.TEST_VIDEO_PATH, max_size=None, skip_reencoding=True)
        start_ts = time.time()
        self.assertEqual(duration, self.TEST_VIDEO_DURATION, 'Duration changed.')
        self.assertEqual(size[0], self.TEST_VIDEO_SIZE[0], 'Width changed.')
        self.assertEqual(size[1], self.TEST_VIDEO_SIZE[1], 'Height changed.')
        end_ts = time.time()
        self.assertLessEqual(end_ts - start_ts, 0.2, 'Skip reencoding is slow')


if __name__ == '__main__':
    unittest.main()
