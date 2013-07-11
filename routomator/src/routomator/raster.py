import os
import pdb

class AsciiRaster(object):
    def __init__(self, filepath):
        print 'Loading raster {}'.format(os.path.basename(filepath))
        with open(filepath, 'rU') as f:
            self.ncols = int(f.readline().strip().split()[1])
            self.nrows = int(f.readline().strip().split()[1])
            self.xll = float(f.readline().strip().split()[1])
            self.yll = float(f.readline().strip().split()[1])
            self.cellsize = float(f.readline().strip().split()[1])
            self.nodata = int(f.readline().strip().split()[1])
            self.raster = [x.strip().split() for x in f.readlines()]
            self.x_bnds = [self.xll + x * self.cellsize for x in range(self.ncols)]
            self.y_bnds = [self.yll + y * self.cellsize for y in range(self.nrows)]
                    
    def __str__(self):
        return 'Ascii Raster object of size {},{} anchored at {},{} with cell size {}'.format(
            self.ncols, self.nrows, self.xll, self.yll, self.cellsize, self.nodata)
        
    def __repr__(self):
        return self.header

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def save(self, outfile):
        print 'Saving raster to {}'.format(os.path.basename(outfile))
        with open(outfile, 'w+') as f:
            f.write(self.header)
            for row in self.raster:
                f.write(' '.join(str(x) for x in row))
                f.write('\n')
        print 'Done saving raster'
            
    def vic_coords(self, (lat, lon)):
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
        return (xi, yi)

    def raster_coords(self, (lat, lon)):
        '''
        Based on an input (lat,lon), this returns the raster index counting from top left
        '''
        print lat, lon
        (xi, yi) = self.vic_coords((lat,lon))
        return (xi, self.nrows - (yi+1))
    
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

    def cell_neighbors(self, (xi, yi)):
        yr = range(max(0, yi-1), min(self.nrows, yi+2))
        xr = range(max(0, xi-1), min(self.ncols, xi+2))
        neighbors = [(i, j) for j in yr for i in xr if (i != xi or j != yi)]
        return neighbors
