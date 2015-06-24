# ffmpeg_wrapper

ffmpeg_wrapper is a very thin client for executing ffmpeg commands from python. the api consists of a single class to inherit: `FFMPEGCommand`.

### command structure

an `FFMPEGCommand` has the following structure `ffmpeg [global_options] [input file options] -i <input file path> [output file options] <output file path>`, and therefore a subclass of `FFMPEGCommand` can take the following class level attributes:

- `which_ffmpeg` -> the fully qualified path to an ffmpeg binary
- `global_options` -> a string containing the global options and flags
- `inputfile_options` -> a string containing options and flags for the input file
- `outputfile_options` -> a string containing options and flags for the output file(s)

and the following instance attributes:

- `inputfile` -> the fully qualified path to the input file to edit
- `*outputfiles` -> one or more output files to apply the command to

for more information see the example command `CreateTestVideo` which creates a blank video file and is incredibly usefull for testing commands.

## NOTICE

you must have compiled ffmpeg in order to use this client. to compile ffmpeg consult the ffmpeg docs, linux distros and mac (via homebrew) should be able to install ffmpeg with additional codecs using a package manager, though i've found its better to install the dependencies manually and then configure ffmpeg with the specific codecs you will be using.
