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
            self.ncols = f.readline().strip().split()[1]
            self.nrows = f.readline().strip().split()[1]
            self.xll = f.readline().strip().split()[1]
            self.yll = f.readline().strip().split()[1]
            self.cellsize = f.readline().strip().split()[1]
            self.nodata = f.readline().strip().split()[1]
            self.raster = [x.strip().split() for x in f.readlines()]
        print 'Done loading raster'

    def to_ascii(self, outfile):
        print 'Saving raster to {}'.format(os.path.basename(outfile))
        with open(outfile, 'w+') as f:
            f.write(self.header)
            for row in self.raster:
                f.write(' '.join(str(x) for x in row))
                f.write('\n')
        print 'Done saving raster'
            
        
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
    with (tempfile.NamedTemporaryFile()) as f:
        r1.to_ascii(f.name)
        r2 = Raster()
        r2.load_ascii(f.name)
        print r2
        print 'Test to see if rasters are equal:{}'.format(r1 == r2)
    
if __name__ == "__main__":
    try:
        test(r'/home/data/projects/hydrology/vic/data/routomator/output/columbia/flow-dir-16th-corrected.asc')
    except Exception, e:
        raise e
