import unittest
import sys
import os

try:
    from instagram_private_api_extensions import media
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api_extensions import media


class TestMedia(unittest.TestCase):

    def test_prepare_image(self):
        _, size = media.prepare_image(
            'http://i.imgur.com/buaMomp.jpg', max_size=(400, 400), aspect_ratios=0.8)
        self.assertLessEqual(size[0], 400, 'Invalid width.')
        self.assertLessEqual(size[1], 400, 'Invalid height.')
        self.assertEqual(1.0 * size[0] / size[1], 0.8, 'Invalid aspect ratio.')

    def test_prepare_image2(self):
        _, size = media.prepare_image(
            'http://i.imgur.com/buaMomp.jpg', max_size=(400, 350), aspect_ratios=(0.8, 1.2))
        self.assertLessEqual(size[0], 400, 'Invalid width.')
        self.assertLessEqual(size[1], 350, 'Invalid height.')
        ar = 1.0 * size[0] / size[1]
        self.assertLessEqual(ar, 1.2)
        self.assertGreaterEqual(ar, 0.8)


if __name__ == '__main__':
    unittest.main()
