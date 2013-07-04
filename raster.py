import os
import pdb

class Raster(object):
    def __init__(self):
        self.raster = []
        self.ncols = None
        self.nrows = None
        self.xll = None
        self.yll = None
        self.cellsize = None
        self.nodata = None
        
    def __str__(self):
        return 'Raster object of size {},{} anchored at {},{} with cell size {}'.format(
            self.ncols, self.nrows, self.xll, self.yll, self.cellsize, self.nodata)
        
    def __repr__(self):
        return self.header

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def parse_ascii(self, s):
        s = s.splitlines()
        self.ncols = int(s[0].strip().split()[1])
        self.nrows = int(s[1].strip().split()[1])
        self.xll = int(s[2].strip().split()[1])
        self.yll = int(s[3].strip().split()[1])
        self.cellsize = float(s[4].strip().split()[1])
        self.nodata = int(s[5].strip().split()[1])
        self.raster = [x.strip().split() for x in s[6:]]
        self.generate_bounds()

    def load_ascii(self, infile):
        print 'Loading raster {}'.format(os.path.basename(infile))
        with open(infile, 'rU') as f:
            self.ncols = int(f.readline().strip().split()[1])
            self.nrows = int(f.readline().strip().split()[1])
            self.xll = int(f.readline().strip().split()[1])
            self.yll = int(f.readline().strip().split()[1])
            self.cellsize = float(f.readline().strip().split()[1])
            self.nodata = int(f.readline().strip().split()[1])
            self.raster = [x.strip().split() for x in f.readlines()]
            self.generate_bounds()
        print 'Done loading raster'

    def save_ascii(self, outfile):
        print 'Saving raster to {}'.format(os.path.basename(outfile))
        with open(outfile, 'w+') as f:
            f.write(self.header)
            for row in self.raster:
                f.write(' '.join(str(x) for x in row))
                f.write('\n')
        print 'Done saving raster'
            
    def generate_bounds(self):
        self.x_bnds = [self.xll + x * self.cellsize for x in range(self.ncols)]
        self.y_bnds = [self.yll + y * self.cellsize for y in range(self.nrows)]
    
    def cell_index(self, lat, lon):
        # based on an input lat/lon, return the i/j cell index from bottom left corner
        max_lon = self.xll + (self.ncols * self.cellsize)
        max_lat = self.yll + (self.nrows * self.cellsize)
        # print "{} < {} < {}: {}".format(self.xll, lon, max_lon, self.xll < lon < max_lon)
        # print "{} < {} < {}: {}".format(self.yll, lat, max_lat, self.yll < lat < max_lat)
        if not self.xll < lon < max_lon:
            raise ValueError('Given lon not contained in raster, lon must be between {} and {}, given {}'.format(self.xll, max_lon, lon))
        if not self.yll < lat < max_lat:
            raise ValueError('Given lat not contained in raster, lat must be between {} and {}, given {}'.format(self.yll, max_lat, lat))
        xi = next(i for i,v in enumerate(self.x_bnds) if v + self.cellsize > lon)
        yi = next(i for i,v in enumerate(self.y_bnds) if v + self.cellsize > lat)
        return yi, xi

    def reset_to_nodata(self):
        self.raster = [[self.nodata for i in xrange(self.ncols)] for j in xrange(self.nrows)]

    def copy_dummy(self):
        import copy
        temp = copy.copy(self)
        temp.reset_to_nodata()
        return temp
    
    @property
    def header(self):
        h = '''NCOLS {0}
NROWS {1}
XLLCORNER {2}
YLLCORNER {3}
CELLSIZE {4}
NODATA_value {5}
'''.format(self.ncols, self.nrows, self.xll, self.yll, self.cellsize, self.nodata)
        return h

    def cell_neighbors(self, xi, yi):
        yr = range(max(0, yi-1), min(self.nrows, yi+2))
        xr = range(max(0, xi-1), min(self.ncols, xi+2))
        neighbors = [(i, j) for j in yr for i in xr if (i != xi or j != yi)]
        return neighbors


def test(f):
    import tempfile
    r1 = Raster()
    r1.load_ascii(f)
    print r1
    print r1.x_bnds
    print r1.y_bnds
    print r1.cell_index(52.65, -125.367)
    print r1.cell_index(47.001, -138.95)
    print r1.cell_index(60.98, -125)
    
    try:
        print r1.cell_index(45,45)
    except ValueError, e:
        print e
        
    print r1.cell_neighbors(0,0)
    print r1.cell_neighbors(50,50)

    with (tempfile.NamedTemporaryFile()) as f:
        r1.save_ascii(f.name)
        r2 = Raster()
        r2.load_ascii(f.name)
        print r2
        print 'Test to see if rasters are equal:{}'.format(r1 == r2)
    
if __name__ == "__main__":
    try:
        test(r'/home/data/projects/hydrology/vic/data/routomator/output/columbia/flow-dir-16th-corrected.asc')
    except Exception, e:
        raise e
