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
        
    def upstream(self):
        raise NotImplemented
        
    def next_downstream_cell(self, source):
        # Returns an xi, yi, tuple of the downstream cell
        direction = self._cell_direction(source)
        if direction == self.nodata or direction == '-9':
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

    @classmethod
    def catchment(cls, lat, lon):
        # based on an input direction raster and a lat/lon, this generates a new raster
        # representing the entire catchment area of that point

        yi, xi = self.cell_index(lat, lon)

        # create a copy with blank data to insert into
        c = cls.copy_dummy()

    def upstream(self, origin):
        for neighbor in c.cell_neighbors(origin):
            print neighbor
            continue
            if flows_into(direction, neighbor, origin):
                upstream(neighbor)

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
0 0 4 3 6 7 4 4 0 0
0 0 3 3 3 3 3 3 3 -9
0 0 2 1 8 7 2 2 0 0
0 0 2 1 8 2 2 0 0 0
0 0 2 1 8 2 0 0 0 0
0 0 0 0 0 0 0 0 0 0
"""
    """Test station data is set so that stations are at:
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 - 0 0 0 0 0
0 0 0 0 0 0 0 0 0 -
0 0 0 - 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
    """
    
    stns = """ID,STATION,LAT,LONG,PROVINCE,GROSS_AREA,EFFECTIVE_
"07EA001","FINLAY RIVER AT WARE",47.34375,-138.71875,"BC",8000,
"07EA002","KWADACHA RIVER NEAR WARE",47.21875,-138.78125,"BC",2410,
"07EA004","INGENIKA RIVER ABOVE SWANNELL RIVER",47.28125,-138.40625,"BC",10000,
"""
    r = DirectionRaster()
    r.parse_ascii(data)

    print r.cell_neighbors(0,0)
    print r.cell_neighbors(5,5)

    print r.next_downstream_cell((3,5))
    print r.all_downstream_cells((3,3))

    import csv
    from StringIO import StringIO

    s = csv.DictReader(StringIO(stns))

    stations = []
    for row in s:
        stations.append(row)

    for stn in stations:
        stn['LAT'] = float(stn['LAT'])
        stn['LONG'] = float(stn['LONG'])
    print stations
    for stn in stations:
        print r.cell_index(stn['LAT'], stn['LONG'])
    
if __name__ == "__main__":
    test()

