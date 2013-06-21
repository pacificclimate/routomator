import os
import pdb

class Raster(object):
    def __init__(self):
        pass

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
        assert self.xll < lon < self.xll + self.ncols * self.cellsize, 'Given lon not contained in raster'
        assert self.yll < lat < self.yll + self.nrows * self.cellsize, 'Given lat not contained in raster'
        xi = next(i for i,v in enumerate(self.x_bnds) if v > lon) - 1
        yi = next(i for i,v in enumerate(self.y_bnds) if v > lat) - 1
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

def test(f):
    import tempfile
    r1 = Raster()
    r1.load_ascii(f)
    print r1
    print r1.x_bnds
    print r1.y_bnds
    print r1.cell_index(52.65, -125.367)
    print r1.cell_index(47.001, -138.95)
    
    try:
        print r1.cell_index(45,45)
    except AssertionError, e:
        print e

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
