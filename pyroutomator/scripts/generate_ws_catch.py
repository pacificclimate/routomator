import os
import argparse
import sys

from subprocess import call

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
    if os.path.exists(ws_shape):
        if args.overwrite:
            try:
                os.remove(ws_shape)
            except:
                raise Exception('Unable to remove hydat file {}, please look into this'.format(ws_shape))
        else:
            raise Exception('File {} already exists, remove it  or use --overwrite before continuing'.format(ws_shape))
    polygonize = [
        'gdal_polygonize.py',
        catch_file,
        '-f', 'ESRI Shapefile',
        ws_shape
        ]
    print 'Calling: {}'.format(' '.join(polygonize))
    call(polygonize)
    print 'DONE'

    hydat_ws = os.path.join(args.tempdir, 'hydat.csv') 
    print 'Clipping hydat stations to catchment area'
    if os.path.exists(hydat_ws):
        if args.overwrite:
            try:
                os.remove(hydat_ws)
            except:
                raise Exception('Unable to remove hydat file {}, please look into this'.format(hydat_ws))
        else:
            raise Exception('File {} already exists, remove it  or use --overwrite before continuing'.format(hydat_ws))

    clip = ['ogr2ogr', '-overwrite', '-clipsrc', ws_shape, '-f', 'CSV', hydat_ws, args.stations, '-lco', 'GEOMETRY=AS_XY']
    print 'Calling: {}'.format(' '.join(clip))
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
    parser.add_argument('-s', '--stations', required=True,
                        help = 'Hydat stations shapefile')
    parser.add_argument('--overwrite', action='store_true',
                        default = False,
                        help = 'If the hydat.csv file already exists in the tempdir, overwrite it')
    args = parser.parse_args()
    main(args)
