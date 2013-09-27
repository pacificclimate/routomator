import math
import argparse
import os

from routomator.raster import AsciiRaster
from routomator.xmask import direction_to_distance

def main(args):
    r = AsciiRaster(args.direction)
    r.raster = direction_to_distance(r)

    r.save(os.path.join(args.outdir, 'xmask.asc'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='XMask file generator')
    parser.add_argument('-d', '--direction',
                        default = r'/datasets/projects-hydrology/routomator/data/output/direction.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-o', '--outdir',
                        default = r'/datasets/projects-hydrology/routomator/data/output',
                        help = 'Directory to store output files, must have write permissions')
    args = parser.parse_args()
    main(args)

