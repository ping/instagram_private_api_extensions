.. instagram_private_api_extensions documentation master file, created by
   sphinx-quickstart on Tue May  2 11:50:20 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

instagram_private_api_extensions
================================

An extension module to `instagram_private_api <https://github.com/ping/instagram_private_api>`_ to help with common tasks such as posting a photo or video.

Features
--------

1. :ref:`api_media`: Edits a photo/video so that it complies with Instagram's requirements by:

    * Resizing
    * Cropping to fit the minimum/maximum aspect ratio
    * Generating the video thumbnail image
    * Clipping the video duration if it is too long
    * Changing the format/encoding

2. :ref:`api_pagination`: Page through an api call such as ``api.user_feed()``.

3. :ref:`api_live`: Download an ongoing IG live stream. Requires `ffmpeg <http://ffmpeg.org/>`_ installed.

3. :ref:`api_replay`: Download an ongoing IG live replay stream. Requires `ffmpeg <http://ffmpeg.org/>`_ installed.

.. toctree::
   :maxdepth: 2
   :caption: Usage

   usage

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   api

.. toctree::
   :caption: Links

   Repository <https://github.com/ping/instagram_private_api_extensions>
   Bug Tracker <https://github.com/ping/instagram_private_api_extensions/issues>
   Tests <https://github.com/ping/instagram_private_api_extensions/tree/master/tests>
