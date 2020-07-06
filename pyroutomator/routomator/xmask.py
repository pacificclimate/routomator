import math
import argparse
import os

from .raster import AsciiRaster

EARTH_CIRCUMFERENCE = 6378137 # earth circumference in meters

def great_circle_distance(latlong_a, latlong_b):
    """
    >>> coord_pairs = [
    ... # between eighth and 31st and eighth and 30th
    ... [(40.750307,-73.994819), (40.749641,-73.99527)],
    ... # sanfran to NYC ~2568 miles
    ... [(37.784750,-122.421180), (40.714585,-74.007202)],
    ... # about 10 feet apart
    ... [(40.714732,-74.008091), (40.714753,-74.008074)],
    ... # inches apart
    ... [(40.754850,-73.975560), (40.754851,-73.975561)],
    ... ]
    >>> for pair in coord_pairs:
    ... great_circle_distance(pair[0], pair[1]) # doctest: +ELLIPSIS
    83.325362855055...
    4133342.6554530...
    2.7426970360283...
    0.1396525521278...
    """
    lat1, lon1 = latlong_a
    lat2, lon2 = latlong_b

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = EARTH_CIRCUMFERENCE * c
    return str(d)

def cell_distance(direction, north, east, south, west):
    """
    Based upon a direction and specific cell bounds, this returns the directional distance in bounds.

    # ArcGIS directions
    # 32  64  128
    # 16  x   1
    # 8   4   2

    GRASS directions
    8   1   2
    7   x   3
    6   5   4
    """

    if direction == '0': return '0'
    # convert numerical grass directions to common format
    replacements = {'1':'N', '2': 'NE', '3': 'E', '4': 'SE', '5': 'S', '6': 'SW', '7': 'W', '8': 'NW'}
    for i, j in replacements.items():
        direction = str(direction).replace(i, j)

    # use midpoint distances when vertical or horizontal direction
    vmid = (math.fabs(north) + math.fabs(south)) / 2
    hmid = (math.fabs(west) + math.fabs(east)) / 2

    if direction in ['N', 'S']:
        return great_circle_distance((north, hmid), (south, hmid))
    if direction in ['NE', 'SW']:
        return great_circle_distance((south, west), (north, east))
    if direction in ['E', 'W']:
        return great_circle_distance((vmid, west), (vmid, east))
    if direction in ['SE', 'NW']:
        return great_circle_distance((north, west), (south, east))
    
def direction_to_distance(r):
    # edit the raster in place fetching distances
    for i in range(int(r.nrows)):
        for j in range(int(r.ncols)):
            r.raster[i][j] = cell_distance(r.raster[i][j], *r.cell_bounds(i, j))
    return r.raster
