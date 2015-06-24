import os.path
from setuptools import setup, find_packages


def read(filename):
    with open(os.path.joi(os.path.dirname(__file__), filename)) as _f:
        contents = _f.read()
    return contents

setup(
    name="ffmpeg_wrapper",
    version="0.1",
    author="andrew young",
    author_email="ayoung@thewulf.org",
    description="a super thin client to call ffmpeg commands from python",
    keywords="ffmpeg audio video",
    long_description=read("README.md"),
    packages=find_packages(exclude=["tests", "test.*"]),
    test_suite="tests",
    install_requires=["six"]
)
