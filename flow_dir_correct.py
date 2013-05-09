import os
import argparse

class BreakIt(Exception): pass

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

    dirs = []
    with open(args.input, 'rU') as f:
        dirs = [x.strip().split() for x in f.readlines()[6:]]
    
    # find all invalid values
    invalids = []
    for i, row in enumerate(dirs):
        for j, value in enumerate(row):
            if value == '-9':
                invalids.append((i, j))
    print invalids

    # fix all invalid values
    for x, y in invalids:
        try:
            print 'Fixing direction {} found at {}, {}'.format(dirs[x][y],x, y)
            neighbors = find_neighbors(dirs, x, y, True)

            for i, j in neighbors:
                try:
                    if dirs[i][j] != '0':
                        dirs[x][y] = find_direction((x,y),(i,j))
                        raise BreakIt
                except IndexError:
                    continue
        except BreakIt:
            pass
    print 'Invalid Directions Fixed'

    header = '''ncols         400
nrows         208
xllcorner     -139
yllcorner     48
cellsize      0.0625
NODATA_value  0
'''
    print 'Saving Output'
    outfile = os.path.join(args.outdir, args.watershed, 'flow-dir-16th-corrected.asc')
    with open(outfile, 'w+') as f:
        f.write(header)
        for row in dirs:
            f.write(" ".join(str(x) for x in row))
            f.write('\n')
    print 'Direction corrected raster saved to: ' + outfile

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
