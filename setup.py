#!/usr/bin/env python
from shotalizer import __version__
from setuptools import setup, find_packages

setup(name="shotalizer",
      version=__version__,
      description="Grab random crops from a set of images",
      author="Chris Malek <cmalek@placodermi.org>",
      author_email="cmalek@placodermi.org",
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),

      entry_points={
        'console_scripts': [
            'shoot = shotalizer.app:main'
        ],
        'shotalizer.main': [
            'crop = shotalizer.commands.crop:CropCommand',
        ],
    },

)
