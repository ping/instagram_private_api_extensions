import os
import time
import hashlib
import io
import re
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.all import resize, crop

from .compat import compat_urllib_request, compat_urlretrieve


def calc_resize(max_size, curr_size):
    """
    Calculate if resize is required based on the max size desired
    and the current size

    :param max_size: tuple of (width, height)
    :param curr_size: tuple of (width, height)
    :return:
    """
    max_width, max_height = max_size
    orig_width, orig_height = curr_size
    if orig_width > max_width or orig_height > max_height:
        resize_factor = min(
            1.0 * max_width / orig_width,
            1.0 * max_height / orig_height)
        new_width = int(resize_factor * orig_width)
        new_height = int(resize_factor * orig_height)
        return new_width, new_height


def calc_crop(aspect_ratios, curr_size):
    """
    Calculate if cropping is required based on the desired aspect
    ratio and the current size.

    :param aspect_ratios: single float value or tuple of (min_ratio, max_ratio)
    :param curr_size: tuple of (width, height)
    :return:
    """
    try:
        if len(aspect_ratios) == 2:
            min_aspect_ratio = float(aspect_ratios[0])
            max_aspect_ratio = float(aspect_ratios[1])
        else:
            raise ValueError('Invalid aspect ratios')
    except TypeError:
        # not a min-max range
        min_aspect_ratio = float(aspect_ratios)
        max_aspect_ratio = float(aspect_ratios)

    curr_aspect_ratio = 1.0 * curr_size[0] / curr_size[1]
    if not min_aspect_ratio <= curr_aspect_ratio <= max_aspect_ratio:
        curr_width = curr_size[0]
        curr_height = curr_size[1]
        if curr_aspect_ratio > max_aspect_ratio:
            # media is too wide
            new_height = curr_height
            new_width = max_aspect_ratio * new_height
        else:
            # media is too tall
            new_width = curr_width
            new_height = new_width / min_aspect_ratio
        left = (curr_width - new_width)/2
        top = (curr_height - new_height)/2
        right = (curr_width + new_width)/2
        bottom = (curr_height + new_height)/2
        return left, top, right, bottom


def is_remote(media):
    if re.match(r'^https?://', media):
        return True
    return False


def prepare_image(img, max_size=(1280, 1280),
                  aspect_ratios=(4.0 / 5.0, 90.0 / 47.0),
                  save_path=None):
    """
    Prepares an image file for posting

    :param img: file path
    :param max_size: tuple of (max_width,  max_height)
    :param aspect_ratios: single float value or tuple of (min_ratio, max_ratio)
    :param save_path: optional output file path
    :return:
    """
    if is_remote(img):
        res = compat_urllib_request.urlopen(img)
        im = Image.open(res)
    else:
        im = Image.open(img)

    new_size = calc_resize(max_size, im.size)
    if new_size:
        im = im.resize(new_size)

    if aspect_ratios:
        crop_box = calc_crop(aspect_ratios, im.size)
        if crop_box:
            im = im.crop(crop_box)

    if im.mode != 'RGB':
        im = im.convert('RGBA')
        im2 = Image.new('RGB', im.size, (255, 255, 255))
        im2.paste(im, (0, 0), im)
        im = im2
    if save_path:
        im.save(save_path)
    b = io.BytesIO()
    im.save(b, 'JPEG')
    return b.getvalue(), im.size


def prepare_video(vid, thumbnail_frame_ts=0.0,
                  max_size=(640, 1137),
                  aspect_ratios=(4.0 / 5.0, 90.0 / 47.0),
                  max_duration=60.0,
                  save_path=None,
                  skip_reencoding=False):
    """
    Prepares a video file for posting

    :param vid: file path
    :param thumbnail_frame_ts: the frame of clip corresponding to time t (in seconds) to be used as the thumbnail
    :param max_size: tuple of (max_width,  max_height)
    :param aspect_ratios: single float value or tuple of (min_ratio, max_ratio)
    :param max_duration: maximum video duration in seconds
    :param save_path: optional output video file path
    :param skip_reencoding: if set to True, the file will not be re-encoded
        if there are no modifications required. Default: False.
    :return:
    """

    vid_is_modified = False

    temp_remote_filename = ''
    if is_remote(vid):
        m = hashlib.md5()
        m.update(vid.encode('utf-8'))
        temp_remote_filename = '%s_%s_%d.tmp.mp4' % (
            os.path.basename(vid).replace('.', ''), m.hexdigest()[:15], int(time.time()))
        compat_urlretrieve(vid, filename=temp_remote_filename)
        vidclip = VideoFileClip(temp_remote_filename)
        vid = temp_remote_filename
    else:
        vidclip = VideoFileClip(vid)

    if vidclip.duration < 3 * 1.0:
        raise ValueError('Duration is too short')

    if vidclip.duration > max_duration * 1.0:
        vidclip = vidclip.subclip(0, max_duration)
        vid_is_modified = False

    if thumbnail_frame_ts > vidclip.duration:
        raise ValueError('Invalid thumbnail frame')

    if max_size:
        new_size = calc_resize(max_size, vidclip.size)
        if new_size:
            vidclip = resize(vidclip, newsize=new_size)
            vid_is_modified = True

    if aspect_ratios:
        crop_box = calc_crop(aspect_ratios, vidclip.size)
        if crop_box:
            vidclip = crop(vidclip, x1=crop_box[0], y1=crop_box[1], x2=crop_box[2], y2=crop_box[3])
            vid_is_modified = True

    vid_filename = os.path.basename(vid)
    ts = int(time.time())
    m = hashlib.md5()
    m.update(('%s.%d' % (vid_filename, int(os.path.getmtime(vid)))).encode('utf-8'))

    temp_video_filename = '%s_%s_%d.tmp.mp4' % (vid_filename.replace('.', ''), m.hexdigest()[:15], ts)
    if save_path:
        if not save_path.lower().endswith('.mp4'):
            raise ValueError('You must specify a .mp4 save path')
        output_file = save_path
    else:
        output_file = temp_video_filename
    if vid_is_modified or not skip_reencoding:
        vidclip.write_videofile(
            output_file, codec='libx264', audio=True, audio_codec='aac', verbose=False)

    temp_thumbnail_filename = '%s_%s_%d.tmp.jpg' % (vid_filename.replace('.', ''), m.hexdigest()[:15], ts)
    vidclip.save_frame(temp_thumbnail_filename, t=thumbnail_frame_ts)

    video_duration = vidclip.duration
    video_size = vidclip.size
    del vidclip      # clear it out

    try:
        with open(temp_thumbnail_filename, mode='r', errors='ignore') as thumb_data:
            video_thumbnail_content = thumb_data.read()
    except TypeError:
        with open(temp_thumbnail_filename, mode='r') as thumb_data:
            video_thumbnail_content = thumb_data.read()

    if vid_is_modified or not skip_reencoding:
        vid_filepath = temp_video_filename if not save_path else save_path
    else:
        vid_filepath = vid
    try:
        with open(vid_filepath, mode='r', errors='ignore') as vid_data:
            video_content = vid_data.read()
    except TypeError:
        with open(vid_filepath, mode='r') as vid_data:
            video_content = vid_data.read()

    # Delete temp files
    if os.path.exists(temp_thumbnail_filename):
        os.remove(temp_thumbnail_filename)
    if not save_path and os.path.exists(temp_video_filename):
        os.remove(temp_video_filename)
    if temp_remote_filename and os.path.exists(temp_remote_filename):
        os.remove(temp_remote_filename)

    if len(video_content) > 50 * 1024 * 1000:
        raise ValueError('Video file is too big')

    return video_content, video_size, video_duration, video_thumbnail_content


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Demo media.py')
    parser.add_argument('-i', '--image', dest='image', type=str)
    parser.add_argument('-v', '--video', dest='video', type=str)

    args = parser.parse_args()

    if args.image:
        photo_data, size = prepare_image(args.image, max_size=(1000, 800), aspect_ratios=0.9)
        print('Image dimensions: %dx%d' % (size[0], size[1]))

    def print_vid_info(video_data, size, duration, thumbnail_data):
        print('vid file size: %d, thumbnail file size: %d, , vid dimensions: %dx%d, duration: %f' %
              (len(video_data), len(thumbnail_data), size[0], size[1], duration))

    if args.video:
        print('Example 1: Resize video to aspect ratio 1, duration 10s')
        video_data, size, duration, thumbnail_data = prepare_video(
            args.video, aspect_ratios=1.0, max_duration=10,
            save_path='example1.mp4')
        print_vid_info(video_data, size, duration, thumbnail_data)

        print('Example 2: Resize video to no greater than 480x480')
        video_data, size, duration, thumbnail_data = prepare_video(
            args.video, thumbnail_frame_ts=2.0, max_size=(480, 480))
        print_vid_info(video_data, size, duration, thumbnail_data)

        print('Example 3: Leave video intact and speed up retrieval')
        video_data, size, duration, thumbnail_data = prepare_video(
            args.video, max_size=None, skip_reencoding=True)
        print_vid_info(video_data, size, duration, thumbnail_data)
