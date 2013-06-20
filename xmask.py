import math
import argparse
import os

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
    for i, j in replacements.iteritems():
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

def cell_coords(i, j, **kwargs):
    ncols = 400
    nrows = 208
    xllcorner = -139
    yllcorner = 48
    cellsize = 0.0625

    max_west = xllcorner
    max_north = yllcorner + (nrows * cellsize)
    cellsize = 0.0625

    cell_north = max_north - (i * cellsize)
    cell_south = cell_north - cellsize

    cell_west = max_west + (j * cellsize)
    cell_east = cell_west + cellsize

    return cell_north, cell_east, cell_south, cell_west
    
def direction_to_distance(dirs):
    params = {
        'ncols': 400,
        'nrows': 208,
        'xllcorner': -139,
        'yllcorner': 48,
        'cellsize': 0.0625
        }
    ncols = 400
    nrows = 208
    xllcorner = -139
    yllcorner = 48
    cellsize = 0.0625

    # edit the table in place fetching distances
    for i in range(nrows):
        for j in range(ncols):
            dirs[i][j] = cell_distance(dirs[i][j], *cell_coords(i, j))
    return dirs

def main(args):
    assert args.watershed is not None, 'Watershed argument missing'
    assert args.input is not None, 'Must provide input direction raster'

    with open(args.input, 'rU') as f:
        dirs = [x.strip().split() for x in f.readlines()[6:]]
    xmask = direction_to_distance(dirs)

    header = '''ncols         400
nrows         208
xllcorner     -139
yllcorner     48
cellsize      0.0625
NODATA_value  0
'''

    outfile = os.path.join(args.outdir, args.watershed, 'xmask.asc')

    with open(outfile, 'wb') as f:
        f.write(header)
        for row in xmask:
            try:
                f.write(' '.join(row))
                f.write('\n')
            except TypeError, e:
                pass
        print 'File saved to: ' + outfile

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='XMask file creator')
    parser.add_argument('-i', '--input',
                        default = None,
                        help = 'Input direction ascii')
    parser.add_argument('-o', '--outdir',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/output',
                        help = 'Base directory you would like to put the output folder')
    parser.add_argument('-w', '--watershed',
                        default = None,
                        help = 'Watershed being processed.  Necessary to determine output folder')
    args = parser.parse_args()
    main(args)

