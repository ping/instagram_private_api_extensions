import unittest
import sys
import os
import shutil

try:
    from instagram_private_api_extensions import replay
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api_extensions import replay


MPD_CONTENT = '''<?xml version="1.0" ?>
<MPD maxSegmentDuration="PT0H0M2.000S" mediaPresentationDuration="PT0H0M5.002S" minBufferTime="PT1.500S" profiles="urn:mpeg:dash:profile:isoff-on-demand:2011,http://dashif.org/guidelines/dash264" type="static"
    xmlns="urn:mpeg:dash:schema:mpd:2011">
    <Period duration="PT0H0M5.002S">
        <AdaptationSet lang="und" segmentAlignment="true" subsegmentAlignment="true" subsegmentStartsWithSAP="1">
            <Representation audioSamplingRate="44100" bandwidth="50598" codecs="mp4a.40.2" id="1" mimeType="audio/mp4" startWithSAP="1">
                <AudioChannelConfiguration schemeIdUri="urn:mpeg:dash:23003:3:audio_channel_configuration:2011" value="2"/>
                <BaseURL>http://127.0.01:8000/replay_audio.mp4</BaseURL>
            </Representation>
        </AdaptationSet>
        <AdaptationSet lang="und" maxFrameRate="16000/528" maxHeight="704" maxWidth="396" par="396:704" segmentAlignment="true" subsegmentAlignment="true" subsegmentStartsWithSAP="1">
            <Representation FBQualityClass="sd" FBQualityLabel="396w" bandwidth="762528" codecs="avc1.4d401f" frameRate="16000/528" height="704" id="2" mimeType="video/mp4" sar="1:1" startWithSAP="1" width="396">
                <BaseURL>http://127.0.01:8000/replay_video.mp4</BaseURL>
            </Representation>
        </AdaptationSet>
    </Period>
</MPD>'''   # noqa


class TestReplay(unittest.TestCase):
    """Tests for replay related functions."""

    @classmethod
    def setUpClass(cls):
        for f in ('output_replay', 'output_replay_cleartempfile',
                  'output_replay_skipffmpeg', 'output_replay_badffmpeg'):
            if os.path.isfile(f):
                os.remove(f)
        for fd in ('output_replay.mp4', 'output_replay_cleartempfile.mp4',
                   'output_replay_skipffmpeg.mp4', 'output_replay_badffmpeg.mp4'):
            if os.path.exists(fd):
                shutil.rmtree(fd, ignore_errors=True)

    def test_downloader(self):
        dl = replay.Downloader(
            mpd=MPD_CONTENT,
            output_dir='output_replay')

        output_file = 'output_replay.mp4'
        dl.download(output_file)
        self.assertTrue(os.path.isfile(output_file), '{0!s} not generated'.format(output_file))

    def test_downloader_cleartempfiles(self):
        dl = replay.Downloader(
            mpd=MPD_CONTENT,
            output_dir='output_replay_cleartempfile')

        output_file = 'output_replay_cleartempfile.mp4'
        dl.download(output_file, cleartempfiles=False)
        self.assertTrue(
            os.path.isfile('output_replay_cleartempfile/replay_video.mp4'),
            'Temp video file was cleared')
        self.assertTrue(
            os.path.isfile('output_replay_cleartempfile/replay_audio.mp4'),
            'Temp audio file was cleared')
        self.assertTrue(os.path.isfile(output_file), '{0!s} not generated'.format(output_file))

    def test_downloader_skipffmpeg(self):
        dl = replay.Downloader(
            mpd=MPD_CONTENT,
            output_dir='output_replay_skipffmpeg')

        output_file = 'output_replay_skipffmpeg.mp4'
        dl.download(output_file, cleartempfiles=True)
        self.assertFalse(
            os.path.isfile('output_replay_skipffmpeg/replay_video.mp4'),
            'Temp video file was not cleared')
        self.assertFalse(
            os.path.isfile('output_replay_skipffmpeg/replay_audio.mp4'),
            'Temp audio file was not cleared')
        self.assertTrue(os.path.isfile(output_file), '{0!s} not generated'.format(output_file))

    def test_downloader_badffmpeg(self):
        dl = replay.Downloader(
            mpd=MPD_CONTENT,
            output_dir='output_replay_badffmpeg',
            user_agent=None,
            ffmpeg_binary='ffmpegbad')

        output_file = 'output_replay_badffmpeg.mp4'
        dl.download(output_file, cleartempfiles=True)
        self.assertTrue(
            os.path.isfile('output_replay_badffmpeg/replay_video.mp4'),
            'Temp video file was cleared')
        self.assertTrue(
            os.path.isfile('output_replay_badffmpeg/replay_audio.mp4'),
            'Temp audio file was cleared')
        self.assertFalse(os.path.isfile(output_file), '{0!s} generated'.format(output_file))


if __name__ == '__main__':
    unittest.main()
