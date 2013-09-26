import os
import argparse
import sys

from routomator.raster import AsciiRaster, DirectionRaster

def main(args):
    sys.setrecursionlimit(10000)

    if args.watershed is None: assert 'Watershed argument missing'

    d = DirectionRaster(args.direction)
    l = tuple(float(x) for x in args.location.split(','))
    print 'Generating catchment for location lat:{} lon:{}'.format(l[0], l[1])
    catchment_area = d.catchment_mask(d.raster_coords(l))
    del(d)
    catch_file = os.path.join(args.tempdir, 'ws.asc')
    catchment_area.save(catch_file)
    del(catchment_area)
    print 'Catchement area creation complete'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Routomator master script')

    parser.add_argument('-d', '--direction',
                        default = r'/datasets/projects-hydrology/routomator/data/input/flow-dir-15.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-l', '--location',
                        default = '49.2270,-121.8400',
                        help = 'Location to create input watershed from of format (-)dd.dddd,(-)dd.dddd (Long,Lat)')
    parser.add_argument('-w', '--watershed',
                        default = None, required=True,
                        help = 'Watershed being processed.  Necessary to determine output folder')
    parser.add_argument('-t', '--tempdir',
                        default = r'/datasets/projects-hydrology/routomator/data/tempfiles',
                        help = 'Directory to store intermediate files, must have write permissions')
    args = parser.parse_args()
    main(args)
