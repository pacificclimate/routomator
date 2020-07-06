from .raster import AsciiRaster

class BreakIt(Exception):
    # Custom exception class to break out of nested loop
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

def find_neighbors(dirs, x, y):
    yr = range(y-1, y+2)
    xr = range(x-1, x+2)
    neighbors = [(i, j) for j in yr for i in xr if (i != x or j != y)]
    return neighbors

def correct_edge_flows(r):

    # first find all flows with -9 direction
    invalids = []
    for i, row in enumerate(r.raster):
        for j, value in enumerate(row):
            if value == '-9':
                invalids.append((i, j))

    # fix all invalid values
    for x, y in invalids:
        try:
            neighbors = find_neighbors(r.raster, x, y)

            for i, j in neighbors:
                try:
                    if r.raster[i][j] != '0':
                        r.raster[x][y] = find_direction((x,y),(i,j))
                        raise BreakIt # Use custom excpetion to jump out of nested loop
                except IndexError:
                    continue
        except BreakIt:
            pass
