import os
import operator

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

class DirectionRaster(AsciiRaster):    
    def __init__(self, filepath):
        super(DirectionRaster, self).__init__(filepath)
        """
        GRASS directions
        8   1   2
        7   x   3
        6   5   4
        """

        self.cardinal = {'1':'N', '2': 'NE', '3': 'E', '4': 'SE', '5': 'S', '6': 'SW', '7': 'W', '8': 'NW'}
        self.numerical = {'N': '1', 'NE': '2', 'E': '3', 'SE': '4', 'S': '5', 'SW': '6', 'W': '7', 'NW': '8'}
        self.print_replace = {'1':'|', '2': '/', '3': '-', '4': r'\\', '5': '|', '6': '/', '7': '-', '8': r'\\'}

        # cell difference Y vaules are counterintuitive...
        # based on row index from TOP LEFT
        self.cell_diff = {'8': (-1,-1), '1':(0,-1),  '2': (1,-1),
                          '7': (-1, 0),            '3': (1,0),
                          '6': (-1,1),'5': (0,1),'4': (1,1)
                          }
    
    def _rerserve_dir(self, d):
        raise NotImplemented

    def _cell_direction(self, cell):
        return self.raster[cell[1]][cell[0]]
    
    def reverse_flow(self):
        raise NotImplemented
        
    def next_downstream_cell(self, source):
        # Returns an xi, yi, tuple of the downstream cell
        direction = self._cell_direction(source)
        if direction == str(self.nodata) or direction == '-9':
            return None
        return(tuple(map(operator.add, source, self.cell_diff[direction])))

    def all_downstream_cells(self, cell):
        # Returns a list of tuples containing all the downstream cells from the source
        next_cell = self.next_downstream_cell(cell)
        print cell, next_cell
        if not next_cell:
            return [cell]
        else:
            return [cell] + self.all_downstream_cells(next_cell)
        
    def is_downstream(self, source, dest):
        # takes xi,yi tuples and returns True if the flow direction connects source to dest

        # basic check if adjacent cells
        xdiff, ydiff = map(operator.sub, dest, source)
        assert (-1 <= xdiff <= 1) and (-1 <= ydiff <= 1), "Direction can only be calculated on adjacent cells"

        return dest == self.next_downstream_cell(source)

    def catchment(self, source):
        # based on an input direction raster and a lat/lon, this generates a new raster
        # representing the entire catchment area of that point

        temp = self.copy_dummy()

        for cell in self.all_upstream_cells(source):
            temp.raster[cell[1]][cell[0]] = 1
        temp.raster[source[1]][source[0]] = 2
        return temp

    def print_raster(self):
        for row in self.raster:
            print row
            
    def print_directions(self):
        printable = []
        for row in self.raster:
            # print row
            new_row = []
            for val in row:
                old_val = val
                for i, j in self.print_replace.iteritems():
                    val = str(val).replace(i, j)
                    
                # print '{} replaced with {}'.format(old_val, val)
                # print val
                new_row.append(val[0])
                # print new_row
            printable.append(new_row)

        for row in printable:
            print ' '.join(row)
        
    def directly_upstream_cells(self, source):
        res = []
        for neighbor in self.cell_neighbors(source):
            # print '{} -> {} in direction {}'.format(neighbor, source, self._cell_direction(neighbor)),
            if self.is_downstream(neighbor, source):
                # print 'yes'
                res.append(neighbor)
                # print res
            else:
                # print ''
                continue
        return res

    def all_upstream_cells(self, source):
        up_neighbors = self.directly_upstream_cells(source)
        if not up_neighbors:
            return [source]
        else:
            up_cells = []
            for up_neighbor in up_neighbors:
                up_cells.extend(self.all_upstream_cells(up_neighbor))
            return [source] + up_cells


    def count(self):
        count = 0
        for row in self.raster:
            for val in row:
                if val != self.nodata:
                    count += 1
        return count
    
    def upstream_stations(self, source):

        pass

    def y_coord_to_vic(self, yi):
        return self.nrows - (yi+1)
        pass
    
    def station_file(self):
        stnlist = sorted(self.stations, key=lambda k:k['count'])
        for stn in stnlist:
            xi, yi = self.cell_index(stn['LAT'], stn['LONG'])
            yi = self.y_coord_to_vic(yi)
            print '1\t0\t{stn}\t{xi}\t{yi}\t-999\t0\nNONE'.format(stn=station_id(stn['STATION']), xi=xi, yi=yi)

    def union(self, other):
        for i in range(self.nrows):
            for j in range(self.ncols):
                if self.raster[i][j] != self.nodata:
                    continue
                else:
                    self.raster[i][j] = other.raster[i][j]
                
    def print_subbasin(self, station):
        print 'Subbasin mask for {}'.format(station)
        a = self.catchment((3,6))
        b = self.catchment((3,3))
        a.print_raster()
        print '#################'
        b.print_raster()
        a.union(b)
        print '#################'
        a.print_raster()
        a.save_ascii('/tmp/' + station + '.ascii')
