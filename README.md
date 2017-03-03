# Instagram Private API Extensions

An extension module to [instagram\_private\_api](https://github.com/ping/instagram_private_api) to help with common tasks such as posting a photo or video.

![](https://img.shields.io/badge/Python-2.7-green.svg)
![](https://img.shields.io/badge/Python-3.5-green.svg)
![License](https://img.shields.io/badge/license-MIT_License-blue.svg)

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

Get a copy of the source via git or download a [tarball](https://github.com/ping/instagram_private_api_extensions/tarball/master) or [zip](https://github.com/ping/instagram_private_api_extensions/zipball/master).
 
```bash
$ git clone git@github.com:ping/instagram_private_api_extensions.git
```

Then install the dependencies (moviepy, pillow) required.

```bash
$ pip install -r requirements.txt
```

Alternatively, you can try installing via pip but this is not recommended since it relies on deprecated functions.

```bash
$ pip install git+ssh://git@github.com/ping/instagram_private_api_extensions.git --process-dependency-links --allow-all-external
```

### Important: Patching MoviePy
[MoviePy](https://github.com/Zulko/moviepy) (as of [``v0.2.2.13``](https://github.com/Zulko/moviepy/tree/v0.2.2.13) or defined in [requirements.txt](requirements.txt)/[setup.py](setup.py)) requires a few unmerged patches to work with this extension

1. [PR #345](https://github.com/Zulko/moviepy/pull/345) because Instagram videos require the AAC audio codec. Patch your copy of MoviePy by [**adding ``aac`` here**](https://github.com/Zulko/moviepy/pull/345/files#diff-9c472ac33610ecc9a98fad3cce9636c2L140) in ``moviepy/tools.py`` if [#345](https://github.com/Zulko/moviepy/pull/345) has not been merged.

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
photo_data, photo_size = media.prepare_image('pathto/my_photo.jpg')
api.post_photo_story(photo_data, photo_size, aspect_ratios=api.reel_ratios())

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

### [Live](instagram_private_api_extensions/live)

```python
from instagram_private_api_extensions import live

broadcast = api.broadcast_info('1234567890')

dl = live.Downloader(
    mpd=broadcast['dash_playback_url'],
    output_dir='output_%s/' % str(broadcast['id']))
try:
    dl.run()
except KeyboardInterrupt:
    if not dl.is_aborted:
        dl.is_aborted = True
        dl.stop()
finally:
    # combine the downloaded files
    # Requires ffmpeg installed. If you prefer to use avconv
    # for example, omit this step and do it manually
    dl.stitch('my_video.mp4')
```
