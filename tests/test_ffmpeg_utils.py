# tests/test_ffmpeg_utils.py
# author: andrew young
# email: ayoung@thewulf.org

from __future__ import absolute_import, print_function, unicode_literals

import os
import mimetypes
from unittest import TestCase
import uuid

from ffmpeg_wrapper import TestVideo


class TestFFMPEGWrapper(TestCase):
    """ making sure things work ...
    """
    @classmethod
    def setUpClass(cls):
        cls.test_video = TestVideo(inputfile="/dev/zero",
            outputfile="/tmp/{title}.mpeg".format(title=uuid.uuid1()))
        with cls.test_video as process:
            print("creating video")
            process.join()  # hang out here until the test video is created

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_video.outputfile)

    def test_video_was_created(self):
        self.assertTrue(os.path.exists(self.test_video.outputfile))

    def test_video_has_correct_mimetype(self):
        filetype, _ = mimetypes.guess_type(self.test_video.outputfile)
        self.assertEqual("video/mpeg", filetype)

