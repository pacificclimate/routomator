import operator
from raster import Raster

class Direction(Raster):    
    """
    GRASS directions
    8   1   2
    7   x   3
    6   5   4
    """
    self.cardinal = {'1':'N', '2': 'NE', '3': 'E', '4': 'SE', '5': 'S', '6': 'SW', '7': 'W', '8': 'NW'}
    self.numerical = {'N': '1', 'NE': '2', 'E': '3', 'SE': '4', 'S': '5', 'SW': '6', 'W': '7', 'NW': '8'}
self.cell_diff = {'8': (-1,1), '1':(0,1),  '2': (1,1),
                  '7': (-1, 0),            '3': (1,0),
                  '6': (-1,-1),'5': (0,-1),'4': (1,-1)
                  }
    
    def _rerserve_dir(self, d):
        raise NotImplemented
    
    def reverse_flow(self):
        raise NotImplemented
        
    def upstream():
        raise NotImplemented
        
    def downstream_cell(self, source, direction):
        # Returns an xi, yi, tuple of the downstream cell
        return(tuple(map(operator.add, source, self.cell_diff[direction])))
    
    def flows_into(direction, source, dest):
        # takes xi,yi tuples and returns True if the flow direction connects source to dest

        xdiff, ydiff = map(operator.sub, dest, source)
        assert (-1 <= xdiff <= 1) AND (-1 <= ydiff <= 1), "Direction can only be calculated on adjacent cells"
        
        if xdiff < 0:
            if ydiff < 0: return '6'
            if ydiff == 0: return '7'
            if ydiff > 0: return '8'
        if xdiff == 0:
            if ydiff < 0: return '5'
            if ydiff > 0: return '1'
        if xdiff > 0:
            if ydiff < 0: return '4'
            if ydiff == 0: return '3'
            if ydiff > 0: return '2'

    @classmethod
    def catchment(cls, lat, lon):
        # based on an input direction raster and a lat/lon, this generates a new raster
        # representing the entire catchment area of that point

        yi, xi = self.cell_index(lat, lon)

        # create a copy with blank data to insert into
        c = cls.copy_dummy()

    def upstream(origin):
        for neighbor in c.cell_neighbors(origin):
            print neighbor
            continue
            if flows_into(direction, neighbor, origin):
                upstream(neighbor)
                

def test(f):
    r = Raster()
    r1.load_ascii(f)
        
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
