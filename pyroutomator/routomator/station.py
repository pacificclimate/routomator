import os

class Station(object):
    def __init__(self, long_name, lat, lon, short_name=None, stn_id=None):
        if type(lat) != float or type(lon) != float:
            raise TypeError, 'Station lat/lon must be of type float'
        self.long_name = long_name
        self.stn_id = stn_id
        if short_name:
            self.short_name = short_name
        else:
            words = self.long_name.split()[:5]
            if len(words) >= 5:
                self.short_name = ''.join([x[0] for x in words])
            else:
                suffix = ''.join([x[0] for x in words[1:]])
                prefix = words[0][:(6-len(words))]
                self.short_name = prefix + suffix
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return '{ln} ({sn}) at {lat}, {lon}'.format(ln = self.long_name, sn = self.short_name, lat = self.lat, lon = self.lon)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def catchment(self, r):
        '''
        Based on an input DirectionRaster, counts the number of cells flowing into the station's cell
        '''

        return len(r.all_upstream_cells(self.raster_coords(r)))

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
            stn_id = row.get('ID', None)
            stations.append(Station(row['STATION'], float(row['LAT']), float(row['LONG']), stn_id=stn_id))
    return stations

def load_stations_w_shortnames(station_csv):
    '''
    Loads the station list from an open file like object
    '''
    import csv
    with open(station_csv, 'r') as f:
        s = csv.DictReader(f)
    
        stations = []
        for row in s:
            stations.append(Station(row['STATION'], float(row['LAT']), float(row['LONG']), row['SHORTNAME']))
    return stations


def directly_downstream_station(station_list, (xi, yi), dir_raster):
    station_coords = [station.raster_coords(dir_raster) for station in station_list]
    next_cell = dir_raster.next_downstream_cell((xi, yi))
    while next_cell is not None:
        if next_cell in station_coords:
            return next_cell
        else: 
            next_cell = dir_raster.next_downstream_cell(next_cell)
    return None

def generate_upstream_station_dict(station_list, dir_raster):
    from collections import defaultdict
    d = defaultdict(list)
    for station in station_list:
        coords = station.raster_coords(dir_raster)
        ds_station = directly_downstream_station(station_list, coords, dir_raster)
        if ds_station == None:
            continue
        d[ds_station].append(coords)
    return d

def generate_single_subbasin_mask(upstream_stations, dir_raster):
    temp_raster = dir_raster.copy_dummy()
    for station in upstream_stations:
        station_catch = dir_raster.catchment(station)
        temp_raster.union(station_catch)
    return temp_raster

def generate_subbasin_masks(station_list, dir_raster, outdir):
    upstream = generate_upstream_station_dict(station_list, dir_raster)
    
    headwater_stations = [station for station in station_list if station.raster_coords(dir_raster) not in upstream.keys()]
    for station in headwater_stations:
        temp_raster = dir_raster.copy_dummy()
        temp_raster.save(os.path.join(outdir, station.short_name + '_subbasin_headwater.asc'))
        del(temp_raster)

    interior_stations = [station for station in station_list if station.raster_coords(dir_raster) in upstream.keys()]
    for station in interior_stations:
        temp_raster = generate_single_subbasin_mask(upstream[station.raster_coords(dir_raster)], dir_raster)
        temp_raster.save(os.path.join(outdir, station.short_name + '_subbasin_interior.asc'))
        del(temp_raster)

def generate_station_file(station_list, dir_raster):
    for stn in station_list:
        stn.count = stn.catchment(dir_raster)
    station_list = sorted(station_list, key=lambda k:k.count, reverse=True)
    s = ''
    for stn in station_list:
        (xi, yi) = stn.vic_coords(dir_raster)
        s += '1\t0\t{stn}\t{xi}\t{yi}\t-999\t0\nNONE\n'.format(stn=stn.short_name, xi=xi, yi=yi)
    return s

def find_station_by_coords(station_list, (xi, yi)):
    raise NotImplemented

def shortname_conflicts(station_list):
    long_names = [stn.long_name for stn in station_list]
    short_names = [stn.short_name for stn in station_list]
    if len(set(short_names)) == len(set(long_names)):
        return False
    else: 
        return True

def generate_shortnames(station_list):
    '''
    Documentations...
    '''
    # First try to use frist letter of all words
    long_names = [stn.long_name for stn in station_list]
    short_names = [x[:5] for x in long_names]
    if len(long_names) == len(set(short_names)):
        for  (stn, name) in zip(station_list, short_names):
            stn.short_name = name
            return station_list

    # Find which names have overlap
    s = set()
    conflicts = []
    for short_name in short_names:
        if short_name in s:
            conflicts += short_name
        s.add(short_name)

    return station_list

if __name__ == '__main__':
    raise RuntimeError
