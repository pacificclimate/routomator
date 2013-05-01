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

def main(args):
    dirs = []
    with open(args.input, 'rU') as f:
        dirs = [x.strip().split(' ') for x in f.readlines()[6:]]
    
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
            print x, y
            neighbors = [(i, j) for j in range(y-1, y+2) for i in range(x-1, x+2) if (i != x or j != y)]
            print neighbors
            for i, j in neighbors:
                try:
                    if dirs[i][j] != '0':
                        dirs[x][y] = find_direction((x,y),(i,j))
                        raise BreakIt
                except IndexError:
                    continue
        except BreakIt:
            pass

    header = '''ncols         400
nrows         208
xllcorner     -139
yllcorner     48
cellsize      0.0625
NODATA_value  0
'''

    with open(args.output, 'wb') as f:
        f.write(header)
        for row in dirs:
            f.write(' '.join(row))
            f.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flow direction corrector')
    parser.add_argument('-i', '--input',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/tempfiles/flow-dir-16th.asc',
                        help = 'Input direction ascii')
    parser.add_argument('-o', '--output',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/output/flow-dir-16th-corrected.asc',
                        help = 'Base directory you would like to put the output folder')
    args = parser.parse_args()
    main(args)
