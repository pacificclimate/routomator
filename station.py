class Station(object):
    def __init__(self, long_name, lat, lon, short_name=None):
        if type(lat) != float or type(lon) != float:
            raise TypeError, 'Station lat/lon must be of type float'
        self.long_name = long_name
        self.short_name = short_name
        self.lat = lat
        self.lon = lon

    def raster_coords(self, r):
        '''
        Converts station lat/lon to raster xi/yi (anchor upper left) based on the
        metadata of an input raster
        '''

        max_lon = r.xll + (r.ncols * r.cellsize)
        max_lat = r.yll + (r.nrows * r.cellsize)
        # print "{} < {} < {}: {}".format(self.xll, lon, max_lon, self.xll < lon < max_lon)
        # print "{} < {} < {}: {}".format(self.yll, lat, max_lat, self.yll < lat < max_lat)

        if not r.xll < lon < max_lon:
            raise ValueError('Given lon not contained in raster, lon must be between {} and {}, given {}'.format(r.xll, max_lon, lon))
        if not r.yll < lat < max_lat:
            raise ValueError('Given lat not contained in raster, lat must be between {} and {}, given {}'.format(r.yll, max_lat, lat))

        xi = next(i for i,v in enumerate(r.x_bnds) if v + r.cellsize > lon)
        yi = next(i for i,v in enumerate(r.y_bnds) if v + r.cellsize > lat)
        return (xi, yi)
        
    def vic_coords(self, r):
        '''
        Converts station lat/lon to vic raster xi/yi (anchor lower left) based on the
        metadata of an input raster
        '''

        (xi, yi) = raster_coords(r)
        return (xi, r.nrows - (yi+1))

def load_stations(station_list):
    '''
    Loads the station list from an open file like object
    '''
    import csv
    s = csv.DictReader(station_list)
    
    stations = []
    for row in s:
        stations.append(Station(row['STATION'], float(row['LAT']), float(row['LONG'])))
    return stations

def validate_station_names(station_list):
    raise NotImplemented

if __name__ == '__main__':
    raise RuntimeError
