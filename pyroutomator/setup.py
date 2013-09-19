import os
from setuptools import setup, find_packages

__version__ = (0, 0, 2)


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Routomator",
    version='.'.join(str(d) for d in __version__),
    author = "Basil Veerman",
    author_email = "bveerman@uvic.ca",
    description = ("VIC routing automation package"),
    keywords = "pcic hydrology dem raster routing",
    url="http://www.pacificclimate.org/",
    packages=find_packages('routomator'),
    scripts = ['scripts/routobot.py'],
#    requires=['pylumberjack (>=1.0)'],
    long_description=read('README')
    )
