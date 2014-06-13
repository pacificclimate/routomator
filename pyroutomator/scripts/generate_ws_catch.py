import os
import argparse
import sys

from routomator.raster import AsciiRaster, DirectionRaster

def main(args):
    sys.setrecursionlimit(10000)

    d = DirectionRaster(args.direction)
    l = tuple(float(x) for x in args.location.split(','))
    print 'Generating catchment for location lat:{} lon:{}'.format(l[0], l[1])
    catchment_area = d.catchment_mask(d.raster_coords(l))
    del(d)
    catch_file = os.path.join(args.tempdir, 'ws.asc')
    catchment_area.save(catch_file)
    del(catchment_area)
    print 'DONE'

    print 'Converting catchment area to polygon'
    ws_shape = os.path.join(args.tempdir, 'ws.shp')
    polygonize = [
        'gdal_polygonize.py',
        args.catchment,
        '-f', 'ESRI Shapefile',
        ws_shape
        ]
    call(polygonize)
    print 'DONE'

    print 'Clipping hydat stations to catchment area'
    if os.path.exists(hydat_ws):
        if args.overwrite:
            try:
                os.remove(hydat_ws)
            except:
                raise Exception('Unable to remove hydat file {}, please look into this'.format(hydat_ws))
        else:
            raise Exception('File {} already exists, remove it  or use --overwrite before continuing'.format(hydat_ws))

    clip = ['ogr2ogr', '-overwrite', '-clipsrc', ws_shape, '-f', 'CSV', hydat_ws, args.stations]
    call(clip)
    print 'DONE'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Watershed catchment area generator')

    parser.add_argument('-d', '--direction',
                        default = r'/datasets/projects-hydrology/routomator/data/input/flow-dir-15.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-l', '--location',
                        default = '49.2270,-121.8400',
                        help = 'Location to create input watershed from of format (-)dd.dddd,(-)dd.dddd (Lat,Long)')
    parser.add_argument('-t', '--tempdir',
                        default = r'/datasets/projects-hydrology/routomator/data/tempfiles',
                        help = 'Directory to store intermediate files, must have write permissions')
    parser.add_argument('-s', '--stations',
                        default = r'/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat_gt_500km2_catch_wgs84.shp',
                        help = 'Hydat stations shapefile')
    parser.add_argument('--overwrite', action='store_true',
                        default = False,
                        help = 'If the hydat.csv file already exists in the tempdir, overwrite it')
    args = parser.parse_args()
    main(args)
