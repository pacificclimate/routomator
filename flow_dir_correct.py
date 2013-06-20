import os
import argparse

from raster import Raster

class BreakIt(Exception):
    # Custom exception class to break out of nested loop
    pass

def find_invalids():
    pass

def find_direction((x,y), (i,j)):
    '''
    GRASS directions
    8   1   2
    7   x   3
    6   5   4
    '''

    if i < x:
        if j < y: return '6'
        if j == y: return '7'
        if j > y: return '8'
    if i == x:
        if j < y: return '5'
        if j > y: return '1'
    if i > x:
        if j < y: return '4'
        if j == y: return '3'
        if j > y: return '2'

def find_neighbors(dirs, x, y, verbose=False):
    yr = range(y-1, y+2)
    xr = range(x-1, x+2)
    neighbors = [(i, j) for j in yr for i in xr if (i != x or j != y)]
    
    if verbose:
        for j in yr:
            print [dirs[i][j] for i in xr]

    return neighbors

def main(args):
    if args.watershed is None: assert 'Watershed argument missing'

    r = Raster()
    r.load_ascii(args.input)
    
    # find all invalid values
    invalids = []
    for i, row in enumerate(r.raster):
        for j, value in enumerate(row):
            if value == '-9':
                invalids.append((i, j))
    print invalids

    # fix all invalid values
    for x, y in invalids:
        try:
            print 'Fixing direction {} found at {}, {}'.format(r.raster[x][y],x, y)
            neighbors = find_neighbors(r.raster, x, y, True)

            for i, j in neighbors:
                try:
                    if r.raster[i][j] != '0':
                        r.raster[x][y] = find_direction((x,y),(i,j))
                        raise BreakIt # Use custom excpetion to jump out of nested loop
                except IndexError:
                    continue
        except BreakIt:
            pass
    print 'Invalid Directions Fixed'

    print 'Saving Output'
    outfile = os.path.join(args.outdir, args.watershed, 'flow-dir-16th-corrected.asc')
    r.save_ascii(outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flow direction corrector')
    parser.add_argument('-i', '--input',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/tempfiles/flow-dir-16th.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-w', '--watershed',
                        default = None,
                        help = 'Watershed being processed.  Necessary to determine output folder')
    parser.add_argument('-o', '--outdir',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/output',
                        help = 'Output direction corrected ascii raster')
    args = parser.parse_args()
    main(args)
