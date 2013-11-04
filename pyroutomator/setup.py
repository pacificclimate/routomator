import os
from setuptools import setup, find_packages

__version__ = (0, 0, 5)


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
    scripts = ['scripts/generate_fraction_file.py',
               'scripts/generate_stations_subbasins.py',
               'scripts/generate_vel_diff_file.py',
               'scripts/generate_ws_catch.py',
               'scripts/prep_accumulation.py',
               'scripts/direction_raster_to_point.py',
               'scripts/generate_xmask.py'],
    install_requires=['rpy2'],
    long_description=read('README.txt')
    )
