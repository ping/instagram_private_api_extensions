.. _usage:

Installation
============

Pip
---

Install via pip

.. code-block:: bash

    $ pip install git+ssh://git@github.com/ping/instagram_private_api_extensions.git@0.3.1

Update your install with the latest release

.. code-block:: bash

    $ pip install git+ssh://git@github.com/ping/instagram_private_api_extensions.git@0.3.1 --upgrade

Force an update from source

.. code-block:: bash

    $ pip install git+ssh://git@github.com/ping/instagram_private_api_extensions.git --upgrade --force-reinstall


Source Code
-----------

The library is maintained on GitHub. Feel free to clone the repository.

.. code-block:: bash

    git clone git://github.com/ping/instagram_private_api_extensions.git


Usage
=====


:ref:`media <api_media>`
------------------------

.. code-block:: python

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

    # post a video without reading the whole file into memory
    vid_saved_path, vid_size, vid_duration, vid_thumbnail = media.prepare_video(
        'pathto/my_video.mp4', aspect_ratios=api.standard_ratios(),
        save_path='pathto/my_saved_video.mp4', save_only=True)
    # To use save_only, the file must be saved locally
    # by specifying the save_path
    with open(vid_saved_path, 'rb') as video_fp:
        api.post_video(video_fp, vid_size, vid_duration, vid_thumbnail)


:ref:`pagination <api_pagination>`
----------------------------------

.. code-block:: python

    from instagram_private_api_extensions import pagination

    # page through a feed
    items = []
    for results in pagination.page(api.user_feed, args={'user_id': '123456'}):
        if results.get('items'):
            items.extend(results['items'])
    print(len(items))


:ref:`live <api_live>`
----------------------

.. code-block:: python

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
