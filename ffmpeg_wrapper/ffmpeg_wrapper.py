# /ffmpeg_wrapper/ffmpeg.py
# author: andrew young

import os
import six
import shlex
from subprocess import Popen, PIPE


if six.PY2:
	FileNotFoundError = OSError


class SystemCommandError(Exception): pass


class SystemCommand(object):
    """utility class to wrap the Popen object in
    a convenient interface.
    """
    wraps = Popen

    def __init__(self, command):
        self.command = command
        self.process = None

    def run(self):
        _input = self.process
        for command in self.command.split("|"):
            command = shlex.split(command)
            _input = self.process.stdout if\
                hasattr(self.process, "stdout") else None
            self.process = self.wraps(command, stdin=_input, stdout=PIPE)
        return self.process

    def __getattr__(self, other):
        return getattr(self.process, other)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.command)
    __str__ = __repr__


class CheckFFMPEGMeta(type):
    """a metaclass that checks for the existance
    of ffmpeg before running ffmpeg commands
    """
    def __new__(cls, name, bases, dct):
        super_new = super(CheckFFMPEGMeta, cls).__new__
        which_ffmpeg = dct.get("which_ffmpeg") or "/usr/bin/ffmpeg"
        try:
            check_ffmpeg = Popen([which_ffmpeg])
        # errno ENOENT or which_ffmpeg == None
        except (OSError, FileNotFoundError, TypeError) as e:
            raise SystemCommandError(e)
        else:
            check_ffmpeg.kill()
        finally:
            dct["which_ffmpeg"] = which_ffmpeg
        return super_new(cls, name, bases, dct)

    def __repr__(cls):
        return "<{0}>".format(cls.__name__)
    __str__ = __repr__


class FFMPEGCommand(six.with_metaclass(CheckFFMPEGMeta)):
    """utility class to wrap arbitrary python commands
    into ffmpeg commands. see http://ffmpeg.org/ffmpeg.html
    for usage
    `{ff} {glargs} {inargs} -i {infile} {outargs} {outfile}`
    """
    _wraps = SystemCommand
    which_ffmpeg = None
    global_options = None
    inputfile_options = None
    outputfile_options = None

    def __init__(self, inputfile, *outputfiles):
        if os.path.exists(inputfile):
            self.inputfile = inputfile
        else:
            raise FileNotFoundError("inputfile {0} not found!".format(inputfile))
        self.outputfiles = outputfiles
        for outputfile in self.outputfiles:
            if not os.path.exists(os.path.dirname(outputfile)):
                os.makedirs(os.path.dirname(self.outputfile))

        self.command = self._format_command()
        self.process = self._wraps(self.command)

    def _format_command(self):
        formatted_in = "{ff}".format(ff=self.which_ffmpeg)
        if self.global_options:
            formatted_in += " {glargs}".format(glargs=self.global_options)
        if self.inputfile_options:
            formatted_in += " {inargs}".format(inargs=self.inputfile_options)
        formatted_in += " -i {infile}".format(infile=self.inputfile)
        if self.outputfile_options:
            formatted_out = " ".join(
                ["{outargs} {outfile}".format(
                    outargs=self.outputfile_options,
                    outfile=out) for out in self.outputfiles])
        else:
            formatted_out = " ".join(out for out in self.outputfiles)
        return " ".join((formatted_in, formatted_out))

    def __enter__(self):
        """context mgmt
        """
        return self.run()

    def __exit__(self):
        """cleanup after failures etc...
        """
        return self.kill()

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.command)
    __str__ = __repr__

    def __getattr__(self, other):
        return getattr(self.process, other)


class CreateTestVideo(FFMPEGCommand):
    global_options = "-t 60 -s 640x480 -f rawvideo -pix_fmt rgb24 -r 25"

