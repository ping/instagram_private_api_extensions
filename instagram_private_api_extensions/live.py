import argparse
import logging
import os
import time
import re
import hashlib
import xml.etree.ElementTree
import threading
import glob
import shutil
import subprocess

import requests
try:
    from .compat import compat_urlparse
except ValueError:
    # To allow running in terminal
    from compat import compat_urlparse


logger = logging.getLogger(__file__)


MPD_NAMESPACE = {'mpd': 'urn:mpeg:dash:schema:mpd:2011'}


class Downloader(object):

    USER_AGENT = 'Instagram 10.9.0 (iPhone8,1; iOS 10_2; en_US; en-US; ' \
                 'scale=2.00; gamut=normal; 750x1334) AppleWebKit/420+'
    MPD_DOWNLOAD_TIMEOUT = 2
    DOWNLOAD_TIMEOUT = 15
    DUPLICATE_ETAG_RETRY = 30

    def __init__(self, mpd, output_dir, callback_check=None, singlethreaded=False, user_agent=None, **kwargs):
        """

        :param mpd: URL to mpd
        :param output_dir: folder to store the downloaded files
        :param callback_check: callback function that can be used to check
        on stream status if the downloader cannot be sure that the stream
        is over
        :param singlethreaded: flag to force single threaded downloads.
        Not advisable since this increases the probability of lost segments.
        :return:
        """
        self.mpd = mpd
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.threads = []
        self.downloaders = {}
        self.last_etag = ''
        self.duplicate_etag_count = 0
        self.callback = callback_check
        self.is_aborted = False
        self.singlethreaded = singlethreaded
        self.stream_id = ''
        self.user_agent = user_agent or self.USER_AGENT
        self.mpd_download_timeout = kwargs.pop('mpd_download_timeout', None) or self.MPD_DOWNLOAD_TIMEOUT
        self.download_timeout = kwargs.pop('download_timeout', None) or self.DOWNLOAD_TIMEOUT
        self.duplicate_etag_retry = kwargs.pop('duplicate_etag_retry', None) or self.DUPLICATE_ETAG_RETRY

        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=2, pool_maxsize=25)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        self.session = session

        # to store the duration of the initial buffered sgements available
        self.initial_buffered_duration = 0.0

        # custom ffmpeg binary path, fallback to ffmpeg_binary path in env if available
        self.ffmpeg_binary = kwargs.pop('ffmpeg_binary', None) or os.getenv('FFMPEG_BINARY', 'ffmpeg')

    def run(self):
        """Begin downloading"""
        while not self.is_aborted:
            try:
                mpd, wait = self._download_mpd()

                self._process_mpd(mpd)
                if wait:
                    logger.debug('Sleeping for %ds' % wait)
                    time.sleep(wait)

            except requests.HTTPError as e:
                err_msg = 'HTTPError downloading %s: %s.' % (self.mpd, e)
                if e.response and e.response.status_code > 500:
                    logger.warn(err_msg)
                    time.sleep(5)
                else:
                    logger.error(err_msg)
                    self.is_aborted = True
            except requests.ConnectionError as e:
                # transient error maybe?
                logger.warn('ConnectionError downloading %s: %s. Retrying...' % (self.mpd, e))

        self.stop()

    def stop(self):
        """
        This is usually called automatically by the downloader but if the download process is
        interrupted unexpectedly, e.g. KeyboardInterrupt, you should call this method to gracefully
        close off the download.

        :return:
        """
        self.is_aborted = True
        if not self.singlethreaded:
            logger.debug('Stopping download threads...')
            threads = self.downloaders.values()
            logger.debug('%d of %d threads are alive' % (
                len(list(filter(lambda t: t and t.is_alive(), threads))), len(threads)))
            [t.join() for t in threads if t and t.is_alive()]

    def _download_mpd(self):
        logger.debug('Requesting %s' % self.mpd)
        res = self.session.get(self.mpd, headers={
            'User-Agent': self.user_agent,
            'Accept': '*/*',
        }, timeout=self.mpd_download_timeout)
        res.raise_for_status()

        xml_text = res.text

        # IG used to send this header when the broadcast ended.
        # Leaving it in in case it returns.
        broadcast_ended = res.headers.get('X-FB-Video-Broadcast-Ended', '')
        # Use the cache-control header as indicator that stream has ended
        cache_control = res.headers.get('Cache-Control', '')
        mobj = re.match(r'max\-age=(?P<age>[0-9]+)', cache_control)
        if mobj:
            max_age = int(mobj.group('age'))
        else:
            max_age = 0

        if broadcast_ended:
            logger.debug('Found X-FB-Video-Broadcast-Ended header: %s' % broadcast_ended)
            logger.info('Stream ended.')
            self.is_aborted = True
        elif max_age > 1:
            logger.info('Stream ended (cache-control: %s).' % cache_control)
            self.is_aborted = True
        else:
            # Use etag to detect if the same mpd is received repeatedly
            etag = res.headers.get('etag')
            if not etag:
                # use contents hash as psuedo etag
                m = hashlib.md5()
                m.update(xml_text)
                etag = m.hexdigest()
            if etag and etag != self.last_etag:
                self.last_etag = etag
                self.duplicate_etag_count = 0
            elif etag:
                self.duplicate_etag_count += 1

            # Periodically check callback if duplicate etag is detected
            if self.duplicate_etag_count and (self.duplicate_etag_count % 5 == 0):
                logger.warn('Duplicate etag %s detected %d time(s)' % (etag, self.duplicate_etag_count))
                if self.callback:
                    callback = self.callback
                    try:
                        abort = callback()
                        if abort:
                            logger.debug('Callback returned True')
                            self.is_aborted = True
                    except Exception as e:
                        logger.warn('Error from callback: %s' % str(e))
            # Final hard abort
            elif self.duplicate_etag_count >= self.duplicate_etag_retry:
                logger.info('Stream likely ended (duplicate etag/hash detected).')
                self.is_aborted = True

        xml.etree.ElementTree.register_namespace('', MPD_NAMESPACE['mpd'])
        mpd = xml.etree.ElementTree.fromstring(xml_text)
        minimum_update_period = mpd.attrib.get('minimumUpdatePeriod', '')
        mobj = re.match('PT(?P<secs>[0-9]+)S', minimum_update_period)
        if mobj:
            after = int(mobj.group('secs'))
        else:
            after = 1
        return mpd, after

    def _process_mpd(self, mpd):
        periods = mpd.findall('mpd:Period', MPD_NAMESPACE)
        logger.debug('Found %d period(s)' % len(periods))
        # Aaccording to specs, multiple periods are allow but IG only sends one usually
        for period in periods:
            logger.debug('Processing period %s' % period.attrib.get('id'))
            for adaptation_set in period.findall('mpd:AdaptationSet', MPD_NAMESPACE):
                representations = adaptation_set.findall('mpd:Representation', MPD_NAMESPACE)
                # sort representations by quality and pick best one
                representations = sorted(
                    representations,
                    key=lambda rep: (
                        (int(rep.attrib.get('width', '0')) * int(rep.attrib.get('height', '0'))) or
                        int(rep.attrib.get('bandwidth', '0')) or
                        rep.attrib.get('FBQualityLabel') or
                        int(rep.attrib.get('audioSamplingRate', '0'))),
                    reverse=True)
                representation = representations[0]
                representation_id = representation.attrib.get('id', '')
                logger.debug(
                    'Selected representation with id %s out of %s' % (
                        representation_id,
                        ' / '.join([r.attrib.get('id', '') for r in representations])
                    ))
                segment_template = representation.find('mpd:SegmentTemplate', MPD_NAMESPACE)

                init_segment = segment_template.attrib.get('initialization')
                media_name = segment_template.attrib.get('media')
                timescale = int(segment_template.attrib.get('timescale'))

                # store stream ID
                if not self.stream_id:
                    mobj = re.search(r'\b(?P<id>[0-9]+)\-init', init_segment)
                    if mobj:
                        self.stream_id = mobj.group('id')

                # download init segment
                init_segment_url = compat_urlparse.urljoin(self.mpd, init_segment)
                self._extract(
                    os.path.basename(init_segment),
                    init_segment_url,
                    os.path.join(self.output_dir, os.path.basename(init_segment)))

                # download timeline segments
                segment_timeline = segment_template.find('mpd:SegmentTimeline', MPD_NAMESPACE)
                segments = segment_timeline.findall('mpd:S', MPD_NAMESPACE)

                buffered_duration = 0
                for seg in segments:
                    buffered_duration += int(seg.attrib.get('d'))
                    seg_filename = media_name.replace(
                        '$Time$', seg.attrib.get('t')).replace('$RepresentationID$', representation_id)
                    segment_url = compat_urlparse.urljoin(self.mpd, seg_filename)
                    self._extract(
                        os.path.basename(seg_filename),
                        segment_url,
                        os.path.join(self.output_dir, os.path.basename(seg_filename)))
                if not self.initial_buffered_duration:
                    self.initial_buffered_duration = float(buffered_duration) / timescale
                    logger.debug('Initial buffered duration: %s' % self.initial_buffered_duration)

    def _extract(self, identifier, target, output):
        if identifier in self.downloaders:
            logger.debug('Already downloading %s' % identifier)
            return
        logger.debug('Requesting %s' % target)
        if self.singlethreaded:
            self._download(target, output)
        else:
            # push each download into it's own thread
            t = threading.Thread(target=self._download, name=identifier, args=(target, output))
            t.start()
            self.downloaders[identifier] = t

    def _download(self, target, output):

        retry_attempts = 2      # custom retry for HTTPError
        for i in range(1, retry_attempts + 1):
            try:
                res = self.session.get(target, headers={
                    'User-Agent': self.user_agent,
                    'Accept': '*/*',
                }, timeout=self.download_timeout)
                res.raise_for_status()

                with open(output, 'wb') as f:
                    f.write(res.content)
                break
            except requests.ConnectionError as e:
                logger.error('ConnectionError %s: %s' % (target, e))
                break
            except requests.HTTPError as e:
                err_msg = 'HTTPError %d %s: %s.' % (e.response.status_code, target, e)
                if i < retry_attempts:
                    logger.warn('%s Retrying...' % err_msg)
                else:
                    logger.error(err_msg)

    def _get_file_index(self, filename):
        """ Extract the numbered index in filename for sorting """
        mobj = re.match(r'.+\-(?P<idx>[0-9]+)\.[a-z]+', filename)
        if mobj:
            return int(mobj.group('idx'))
        return -1

    def stitch(self, output_filename,
               skipffmpeg=False,
               cleartempfiles=True):
        """
        Combines all the dowloaded stream segments into the final mp4 file.

        :param output_filename: Output file path
        :param skipffmpeg: bool flag to not use ffmpeg to join audio and video file into final mp4
        :param cleartempfiles: bool flag to remove downloaded and temp files
        """
        if not self.stream_id:
            raise Exception('No stream ID found.')
        audio_stream = os.path.join(self.output_dir, 'source_%s_m4a.tmp' % self.stream_id)
        video_stream = os.path.join(self.output_dir, 'source_%s_mp4.tmp' % self.stream_id)

        with open(audio_stream, 'wb') as outfile:
            logger.debug('Assembling audio stream... %s' % audio_stream)
            # Audio segments are named: '<stream-id>-<numeric-seq-num>.m4a'
            files = list(filter(
                os.path.isfile,
                glob.glob(os.path.join(self.output_dir, '%s-*.m4a' % self.stream_id))))
            files = sorted(files, key=lambda x: self._get_file_index(x))
            for f in files:
                with open(f, 'rb') as readfile:
                    try:
                        shutil.copyfileobj(readfile, outfile)
                    except IOError as e:
                        logger.error('Error processing %s' % f)
                        logger.error(e)
                        raise e

        with open(video_stream, 'wb') as outfile:
            logger.debug('Assembling video stream... %s' % video_stream)
            # Videos segments are named: '<stream-id>-<numeric-seq-num>.m4v'
            files = list(filter(
                os.path.isfile,
                glob.glob(os.path.join(self.output_dir, '%s-*.m4v' % self.stream_id))))
            files = sorted(files, key=lambda x: self._get_file_index(x))
            for f in files:
                with open(f, 'rb') as readfile:
                    try:
                        shutil.copyfileobj(readfile, outfile)
                    except IOError as e:
                        logger.error('Error processing %s' % f)
                        logger.error(e)
                        raise e

        exit_code = 0
        if not skipffmpeg:
            cmd = [
                self.ffmpeg_binary, '-loglevel', 'panic',
                '-i', audio_stream,
                '-i', video_stream,
                '-c:v', 'copy', '-c:a', 'copy', output_filename]
            exit_code = subprocess.call(cmd)

            if exit_code:
                logger.error('ffmpeg exited with the code: %s' % exit_code)
                logger.error('Command: %s' % ' '.join(cmd))

        if cleartempfiles and not exit_code:
            # Specifically only remove this stream's temp files
            for f in glob.glob(os.path.join(self.output_dir, '%s-*.*' % self.stream_id)):
                os.remove(f)

            # Don't del source*.tmp files if not using ffmpeg
            # so that user can still use the source* files with another
            # tool such as avconv
            if not skipffmpeg:
                os.remove(audio_stream)
                os.remove(video_stream)


if __name__ == '__main__':
    """
    Example of how to init and start the Downloader
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('mpd')
    parser.add_argument('-v', action='store_true', help='Verbose')
    parser.add_argument('-s', metavar='OUTPUT_FILENAME',
                        help='Output filename')
    parser.add_argument('-o', metavar='DOWLOAD_DIR',
                        default='output/', help='Download folder')
    args = parser.parse_args()

    if args.v:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logging.basicConfig(level=logger.level)

    dl = Downloader(mpd=args.mpd, output_dir=args.o)
    try:
        dl.run()
    except KeyboardInterrupt as e:
        logger.info('Interrupted')
        if not dl.is_aborted:
            dl.stop()
    finally:
        if args.s:
            dl.stitch(args.s)
