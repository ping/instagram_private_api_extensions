# Instagram Private API Extensions

An extension module to [instagram\_private\_api](https://github.com/ping/instagram_private_api) to help with common tasks such as posting a photo or video.

## Features

Edits a photo/video so that it complies with Instagram's requirements by:

* Resizing
* Cropping to fit the minimum/maximum aspect ratio
* Generating the video thumbnail image
* Clipping the video duration if it is too long
* Changing the format/encoding

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
[MoviePy](https://github.com/Zulko/moviepy) (as of [``d4c9c37``](https://github.com/Zulko/moviepy/tree/d4c9c37bc88261d8ed8b5d9b7c317d13b2cdf62e) or defined in [requirements.txt](requirements.txt)/[setup.py](setup.py)) requires an unmerged [patch (#345)](https://github.com/Zulko/moviepy/pull/345) to work with this extension because Instagram videos require the AAC audio codec. Make sure you manually patch your copy of MoviePy by [**adding ``aac`` here**](https://github.com/Zulko/moviepy/pull/345/files#diff-9c472ac33610ecc9a98fad3cce9636c2L140) in ``moviepy/tools.py`` if [#345](https://github.com/Zulko/moviepy/pull/345) has not been merged.

## Usage
```python
from instagram_private_api import Client
from instagram_private_api_extensions import media

api = Client('your_username', 'your_password')

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
