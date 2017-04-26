# Instagram Private API Extensions

An extension module to [instagram\_private\_api](https://github.com/ping/instagram_private_api) to help with common tasks such as posting a photo or video.

![](https://img.shields.io/badge/Python-2.7-3776ab.svg)
![](https://img.shields.io/badge/Python-3.5-3776ab.svg)
[![Release](https://img.shields.io/badge/release-v0.2.6-orange.svg)](https://github.com/ping/instagram_private_api_extensions/releases)
[![Build](https://img.shields.io/travis/ping/instagram_private_api_extensions.svg)](https://travis-ci.org/ping/instagram_private_api_extensions)
[![Coverage](https://img.shields.io/coveralls/ping/instagram_private_api_extensions.svg)](https://coveralls.io/github/ping/instagram_private_api_extensions)

## Features

1. [``media``](#media): Edits a photo/video so that it complies with Instagram's requirements by:
    * Resizing
    * Cropping to fit the minimum/maximum aspect ratio
    * Generating the video thumbnail image
    * Clipping the video duration if it is too long
    * Changing the format/encoding

2. [``pagination``](#pagination): Page through an api call such as ``api.user_feed()``.

3. [``live``](#live): Download an ongoing IG live stream. Requires ffmpeg installed.

## Install

Install with pip using

```bash
pip install git+ssh://git@github.com/ping/instagram_private_api_extensions.git@0.2.6
```

To update:

```bash
pip install git+ssh://git@github.com/ping/instagram_private_api_extensions.git@0.2.6 --upgrade
```

To update with latest repo code:

```bash
pip install git+ssh://git@github.com/ping/instagram_private_api_extensions.git --upgrade --force-reinstall
```

## Usage

### [Media](instagram_private_api_extensions/media.py)
```python
from instagram_private_api import Client
from instagram_private_api_extensions import media

api = Client('username', 'password')

# post a photo
photo_data, photo_size = media.prepare_image(
    'pathto/my_photo.jpg', aspect_ratios=api.standard_ratios())
api.post_photo(photo_data, photo_size, caption='Hello World!')

# post a video
vid_data, vid_size, vid_duration, vid_thumbnail = media.prepare_video(
    'pathto/my_video.mp4', aspect_ratios=api.standard_ratios())
api.post_video(vid_data, vid_size, vid_duration, vid_thumbnail)

# post a photo story
photo_data, photo_size = media.prepare_image(
    'pathto/my_photo.jpg', aspect_ratios=api.reel_ratios())
api.post_photo_story(photo_data, photo_size)

# post a video story
vid_data, vid_size, vid_duration, vid_thumbnail = media.prepare_video(
    'pathto/my_video.mp4', aspect_ratios=api.reel_ratios())
api.post_video_story(vid_data, vid_size, vid_duration, vid_thumbnail)
```

### [Pagination](instagram_private_api_extensions/pagination.py)

```python
from instagram_private_api_extensions import pagination

# page through a feed
items = []
for results in pagination.page(api.user_feed, args={'user_id': '123456'}):
    if results.get('items'):
        items.extend(results['items'])
print(len(items))
```

### [Live](instagram_private_api_extensions/live.py)

```python
from instagram_private_api_extensions import live

broadcast = api.broadcast_info('1234567890')

dl = live.Downloader(
    mpd=broadcast['dash_playback_url'],
    output_dir='output_%s/' % str(broadcast['id']),
    user_agent=api.user_agent)
try:
    dl.run()
except KeyboardInterrupt:
    if not dl.is_aborted:
        dl.stop()
finally:
    # combine the downloaded files
    # Requires ffmpeg installed. If you prefer to use avconv
    # for example, omit this step and do it manually
    dl.stitch('my_video.mp4')
```

## Support
Make sure to review the [contributing documentation](CONTRIBUTING.md) before submitting an issue report or pull request.
