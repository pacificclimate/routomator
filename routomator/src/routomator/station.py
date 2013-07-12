class Station(object):
    def __init__(self, long_name, lat, lon, short_name=None):
        if type(lat) != float or type(lon) != float:
            raise TypeError, 'Station lat/lon must be of type float'
        self.long_name = long_name
        self.short_name = short_name
        self.lat = lat
        self.lon = lon

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def raster_coords(self, r):
        '''
        Converts station lat/lon to raster xi/yi (anchor upper left) based on the
        metadata of an input raster
        '''

        return r.raster_coords((self.lat, self.lon))
        
    def vic_coords(self, r):
        '''
        Converts station lat/lon to vic raster xi/yi (anchor lower left) based on the
        metadata of an input raster
        '''

        return r.vic_coords((self.lat, self.lon))

def load_stations(station_csv):
    '''
    Loads the station list from an open file like object
    '''
    import csv
    with open(station_csv, 'r') as f:
        s = csv.DictReader(f)
    
        stations = []
        for row in s:
            stations.append(Station(row['STATION'], float(row['LAT']), float(row['LONG'])))
    return stations

def generate_shortnames(station_list):
    '''
    Documentations...
    '''
    raise NotImplemented

if __name__ == '__main__':
    raise RuntimeError
