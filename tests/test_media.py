import unittest
import sys
import os
import tempfile
import io

try:
    from instagram_private_api_extensions import media
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api_extensions import media

from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image


class TestMedia(unittest.TestCase):
    """Tests for emdia related functions."""

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

    def test_prepare_image3(self):
        _, size = media.prepare_image(
            self.TEST_IMAGE_PATH, max_size=(1080, 1350), aspect_ratios=(0.8, 1.2), min_size=(640, 640))
        self.assertLessEqual(size[0], 1080, 'Invalid width (max)')
        self.assertLessEqual(size[1], 1350, 'Invalid height (max).')
        self.assertGreaterEqual(size[0], 640, 'Invalid width (min)')
        self.assertGreaterEqual(size[1], 640, 'Invalid height (min)')
        ar = 1.0 * size[0] / size[1]
        self.assertLessEqual(round(ar, 2), 1.2)
        self.assertGreaterEqual(round(ar, 2), 0.8)

    def test_prepare_image4(self):
        with self.assertRaises(ValueError):
            _, size = media.prepare_image(
                self.TEST_IMAGE_PATH, max_size=(1080, 1350), aspect_ratios=(4.0 / 5), min_size=(1081, 640))

    def test_remote_image(self):
        image_url = 'https://c2.staticflickr.com/6/5267/5669212075_039ed45bff_z.jpg'
        image_data, size = media.prepare_image(
            image_url, max_size=(400, 400), save_path='remote.jpg')
        self.assertLessEqual(size[0], 400, 'Invalid width.')
        self.assertLessEqual(size[1], 400, 'Invalid height.')
        self.assertGreater(len(image_data), 0)

    def test_prepare_video(self):
        vid_returned, size, duration, thumbnail_content = media.prepare_video(
            self.TEST_VIDEO_PATH, aspect_ratios=1.0, max_duration=10, save_path='media/output.mp4',
            save_only=True)
        self.assertEqual(duration, 10.0, 'Invalid duration.')
        self.assertEqual(size[0], size[1], 'Invalid width/length.')
        self.assertTrue(os.path.isfile('media/output.mp4'), 'Output file not generated.')
        self.assertTrue(os.path.isfile(vid_returned), 'Output file not returned.')

        with self.assertRaises(ValueError) as ve:
            media.prepare_video(
                self.TEST_VIDEO_PATH, aspect_ratios=1.0, max_duration=10, save_only=True)
        self.assertEqual(str(ve.exception), '"save_path" cannot be empty.')
        self.assertGreater(len(thumbnail_content), 0, 'No thumbnail content returned.')

        # Save video, thumbnail content and verify attributes
        vidclip_output = VideoFileClip('media/output.mp4')
        self.assertAlmostEqual(duration, vidclip_output.duration, places=1)
        self.assertEqual(size[0], vidclip_output.size[0])
        self.assertEqual(size[1], vidclip_output.size[1])

        im = Image.open(io.BytesIO(thumbnail_content))
        self.assertEqual(size[0], im.size[0])
        self.assertEqual(size[1], im.size[1])

    def test_prepare_video2(self):
        video_content, size, duration, thumbnail_content = media.prepare_video(
            self.TEST_VIDEO_PATH, max_size=(480, 480), min_size=(0, 0))
        self.assertEqual(duration, self.TEST_VIDEO_DURATION, 'Duration changed.')
        self.assertLessEqual(size[0], 480, 'Invalid width.')
        self.assertLessEqual(size[1], 480, 'Invalid height.')
        self.assertEqual(
            1.0 * size[0] / size[1],
            1.0 * self.TEST_VIDEO_SIZE[0] / self.TEST_VIDEO_SIZE[1],
            'Aspect ratio changed.')
        self.assertGreater(len(video_content), 0, 'No video content returned.')
        self.assertGreater(len(thumbnail_content), 0, 'No thumbnail content returned.')

        # Save video, thumbnail content and verify attributes
        video_output = tempfile.NamedTemporaryFile(prefix='ipae_test_', suffix='.mp4', delete=False)
        video_output.write(video_content)
        video_output.close()
        vidclip_output = VideoFileClip(video_output.name)
        self.assertAlmostEqual(duration, vidclip_output.duration, places=1)
        self.assertEqual(size[0], vidclip_output.size[0])
        self.assertEqual(size[1], vidclip_output.size[1])

        im = Image.open(io.BytesIO(thumbnail_content))
        self.assertEqual(size[0], im.size[0])
        self.assertEqual(size[1], im.size[1])

    def test_prepare_video3(self):
        video_content, size, duration, thumbnail_content = media.prepare_video(
            self.TEST_VIDEO_PATH, max_size=None, max_duration=1000.0,
            skip_reencoding=True, min_size=None)

        self.assertEqual(size[0], self.TEST_VIDEO_SIZE[0], 'Width changed.')
        self.assertEqual(size[1], self.TEST_VIDEO_SIZE[1], 'Height changed.')

        self.assertGreater(len(video_content), 0, 'No video content returned.')
        self.assertGreater(len(thumbnail_content), 0, 'No thumbnail content returned.')

        # Save video, thumbnail content and verify attributes
        video_output = tempfile.NamedTemporaryFile(prefix='ipae_test_', suffix='.mp4', delete=False)
        video_output.write(video_content)
        video_output.close()
        vidclip_output = VideoFileClip(video_output.name)
        self.assertAlmostEqual(duration, vidclip_output.duration, places=1)
        self.assertEqual(size[0], vidclip_output.size[0])
        self.assertEqual(size[1], vidclip_output.size[1])

        im = Image.open(io.BytesIO(thumbnail_content))
        self.assertEqual(size[0], im.size[0])
        self.assertEqual(size[1], im.size[1])

        self.assertEqual(
            os.path.getsize(video_output.name),
            os.path.getsize(self.TEST_VIDEO_PATH))

    def test_remote_video(self):
        video_url = 'https://raw.githubusercontent.com/johndyer/mediaelement-files/master/big_buck_bunny.mp4'
        video_content, size, duration, thumbnail_content = media.prepare_video(
            video_url, aspect_ratios=1.0, max_duration=10)
        self.assertEqual(duration, 10.0, 'Invalid duration.')
        self.assertEqual(size[0], size[1], 'Invalid width/length.')
        self.assertGreater(len(video_content), 0, 'No video content returned.')
        self.assertGreater(len(thumbnail_content), 0, 'No thumbnail content returned.')

        # Save video, thumbnail content and verify attributes
        video_output = tempfile.NamedTemporaryFile(prefix='ipae_test_', suffix='.mp4', delete=False)
        video_output.write(video_content)
        video_output.close()
        vidclip_output = VideoFileClip(video_output.name)
        self.assertAlmostEqual(duration, vidclip_output.duration, places=1)
        self.assertEqual(size[0], vidclip_output.size[0])
        self.assertEqual(size[1], vidclip_output.size[1])

        im = Image.open(io.BytesIO(thumbnail_content))
        self.assertEqual(size[0], im.size[0])
        self.assertEqual(size[1], im.size[1])

    def test_helper_methods(self):
        self.assertRaises(ValueError, lambda: media.prepare_video(
            self.TEST_VIDEO_PATH, thumbnail_frame_ts=999.99))
        self.assertRaises(ValueError, lambda: media.prepare_video(
            self.TEST_VIDEO_PATH, save_path='output.mov'))
        self.assertRaises(ValueError, lambda: media.calc_crop((1, 2, 3), (500, 600)))
        box = media.calc_crop((1, 2), (400, 800))
        self.assertEqual(box, (0, 200, 400, 600))


if __name__ == '__main__':
    unittest.main()
