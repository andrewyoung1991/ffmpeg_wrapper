# ffmpeg_wrapper/__init__.py
# author: andrew young
# email: ayoung@thewulf.org

from __future__ import absolute_import, print_function, unicode_literals

import re
import subprocess

from .ffmpeg_wrapper import *


class TestVideo(FFMPEGCommand):
    """ a very usefull class for setting up a test video, perhaps as follows:
    test_vid = CreateTestVideo(inputfile="/dev/null", outputfile="/tmp/test.mpeg")
    """
    global_options = "-t 10 -s 640x480 -f rawvideo -pix_fmt rgb24 -r 25"


# streaming video helpers
class ConvertToMP4(FFMPEGCommand):
    """ converts audio to AAC in a MP4 container
    """
    vcodec_options = "libx264 -profile:v high -preset slow -b:v 500k -maxrate 500k"\
        " -bufsize 1000k -vf scale=480:-1 -threads 0"
    acodec_options = "libfdk_aac -b:a 128k"


class ConvertToWEBM(FFMPEGCommand):
    """ converts audio to OGG in a WEBM container
    """
    vcodec_options = "libvpx -quality good -cpu-used 0 -b:v 600k -maxrate 600k -bufsize"\
        " 1200k -qmin 10 -qmax 42 -vf scale=-1:480 -threads 0"
    acodec_options = "libvorbis -b:a 128k"


def get_ffmpeg_buildconf(which_ffmpeg="/usr/bin/ffmpeg"):
    config = subprocess.check_output([which_ffmpeg, "-buildconf"], ).decode("utf-8")
    return re.findall(r"--enable-([\w-]+)", config)

