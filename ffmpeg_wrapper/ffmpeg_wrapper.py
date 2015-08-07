# ffmpeg_wrapper/ffmpeg_wrapper.py
# author: andrew young
# email: ayoung@thewulf.org

import os
import six
import shlex
from subprocess import Popen, PIPE, DEVNULL
from threading import Thread


if six.PY2:
    FileNotFoundError = OSError


class SystemCommandError(Exception): pass


class SystemCommand(object):
    """ utility class to wrap the Popen object in a convenient interface.
    supports notification of observers when a process has finished.
    """
    wraps = Popen

    def __init__(self, command, observers=None):
        self.command = command
        self.observers = observers
        self.process = None

    def run(self, wait=False):
        """ runs the command in a thread
        """
        def in_background():
            _input = self.process
            for command in self.command.split("|"):
                command = shlex.split(command)
                _input = self.process.stdout if self.process else None
                stdout = PIPE if _input else DEVNULL
                self.process = self.wraps(command, stdin=_input, stderr= stdout,
                    stdout=stdout)
                self.process.communicate()
            self.notify_observers()
            return self.process

        thread = Thread(target=in_background)
        thread.start()

        if wait:
            thread.join()

        return thread

    def kill(self):
        try:
            self.process.kill()
        except ProcessLookupError:
            pass
        else:
            # just to be sure the observers are notified
            self.notify_observers(killed=True)

    def notify_observers(self, killed=False):
        if self.observers:
            for observer in self.observers:
                observer.recieve_notification(self, killed)

    def __getattr__(self, other):
        return getattr(self.process, other)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.command)
    __str__ = __repr__


class CheckFFMPEGMeta(type):
    """ a metaclass that checks for the existance of ffmpeg before running ffmpeg
    commands
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


class ObserverMixin(object):
    def recieve_notification(self, process, killed):
        """ this should be implemented in a subclass
        """
        print(process, "completed!" if not killed else "killed!")


class FFMPEGCommand(six.with_metaclass(CheckFFMPEGMeta, ObserverMixin)):
    """utility class to wrap arbitrary python commands into ffmpeg commands.
    see http://ffmpeg.org/ffmpeg.html for usage
    """
    _wraps = SystemCommand
    which_ffmpeg = None
    global_options = None
    inputfile_options = None
    acodec_options = None
    vcodec_options = None
    outputfile_options = None

    def __init__(self, inputfile, outputfile):
        if os.path.exists(inputfile):
            self.inputfile = inputfile
        else:
            raise FileNotFoundError("inputfile {0} not found!".format(inputfile))
        self.outputfile = outputfile
        if not os.path.exists(os.path.dirname(self.outputfile)):
            os.makedirs(os.path.dirname(self.outputfile))

        self.command = self._format_command()
        self.process = self._wraps(self.command, [self, ])

    def _format_command(self):
        formatted_in = "{ff}".format(ff=self.which_ffmpeg)
        formatted_out = ""
        if self.global_options:
            formatted_in += " {glargs}".format(glargs=self.global_options)
        if self.inputfile_options:
            formatted_in += " {inargs}".format(inargs=self.inputfile_options)
        formatted_in += " -i {infile}".format(infile=self.inputfile)
        if self.vcodec_options:
            formatted_in += " -codec:v {vcargs}".format(vcargs=self.vcodec_options)
        if self.acodec_options:
            formatted_in += " -codec:a {acargs}".format(acargs=self.acodec_options)
        if self.outputfile_options:
            formatted_out += "{outargs} ".format(outargs=self.outputfile_options)
        formatted_out += "{outfile}".format(outfile=self.outputfile)
        return " ".join((formatted_in, formatted_out))

    def __enter__(self):
        """ context mgmt
        """
        process = self.run()
        return process

    def __exit__(self, *args, **kwargs):
        """ cleanup after failures etc...
        """
        return self.kill()

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.command)
    __str__ = __repr__

    def __getattr__(self, other):
        return getattr(self.process, other)

