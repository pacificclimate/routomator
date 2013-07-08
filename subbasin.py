import operator
from raster import Raster

class DirectionRaster(Raster):    
    def __init__(self):
        super(DirectionRaster, self).__init__()
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
        # Grass orders from lower left corner, but array indexed from top
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

    def load_stations(self, station_list):
        # loads the station list from an open file like object
        import csv
        s = csv.DictReader(station_list)

        self.stations = []
        for row in s:
            self.stations.append(row)

        for stn in self.stations:
            stn['LAT'] = float(stn['LAT'])
            stn['LONG'] = float(stn['LONG'])

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
        
def station_id(name):
    return name[:5]

def test(f=None):
    """
    GRASS directions
    8   1   2
    7   x   3
    6   5   4
    """

    data = """ncols 10
nrows 10
xllcorner -139
yllcorner 47
cellsize 0.0625
NODATA_value 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 4 5 6 4 0 0 0 0
0 0 4 5 6 4 4 0 0 0
0 0 4 4 6 5 4 4 0 0
0 0 3 3 3 3 3 3 3 -9
0 0 2 1 8 1 2 2 0 0
0 0 2 1 8 2 2 0 0 0
0 0 2 1 8 2 0 0 0 0
0 0 0 0 0 0 0 0 0 0
"""
    """Test station data is set so that stations are at:
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 - 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 -
0 0 0 - 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
    """
    
    stns = """ID,STATION,LAT,LONG,PROVINCE,GROSS_AREA,EFFECTIVE_
"07EA001","FINLAY RIVER AT WARE",47.40375,-138.78125,"BC",8000,
"07EA002","KWADACHA RIVER NEAR WARE",47.21875,-138.78125,"BC",2410,
"07EA004","INGENIKA RIVER ABOVE SWANNELL RIVER",47.34125,-138.40625,"BC",10000,
"""
    r = DirectionRaster()
    r.parse_ascii(data)

    print r.cell_neighbors((0,0))
    print r.cell_neighbors((5,5))

    print r.next_downstream_cell((3,5))
    print r.all_downstream_cells((3,3))

    import csv
    from StringIO import StringIO

    r.load_stations(StringIO(stns))
    
    print r.stations

    print '#################'    
    for stn in r.stations:
        print stn['STATION']
        source =  r.cell_index(stn['LAT'], stn['LONG'])
        print source
        catchment = r.catchment(source)
        catchment.print_raster()
        print catchment.count()
        stn['count'] = catchment.count()
    print r.stations
    print '#################'

    r.print_directions()
    print 'Upstream of {}:{}'.format((3,3),r.directly_upstream_cells((3,3)))
    print 'Upstream of {}:{}'.format((5,5),r.directly_upstream_cells((5,5)))
    print '#################'
    print r.all_upstream_cells((2,2))
    print r.all_upstream_cells((3,3))
    print r.all_upstream_cells((3,4))
    print '#################'
    r.print_subbasin("INGEN")
    print '#################'
    r.station_file()
    
if __name__ == "__main__":
    test()

