import os
import argparse
import sys
from subprocess import call

from rpy2.robjects import r
from rpy2.robjects.packages import importr

from routomator.raster import AsciiRaster, DirectionRaster
from routomator.direction import correct_edge_flows
from routomator.station import load_stations, generate_shortnames, generate_subbasin_masks

def main(args):
    ws_shape = os.path.join(args.tempdir, 'ws.shp')
    polygonize = ['gdal_polygonize.py', args.catchment, '-f', 'ESRI Shapefile', ws_shape]
#    call(polygonize)

    acc_cut = ['gdalwarp', '-of', 'AAIGrid', '-overwrite', '-cutline', ws_shape, args.accumulation, os.path.join(args.tempdir, 'accumulation_clipped.asc')]
    call(acc_cut)
    exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Routomator master script')

    parser.add_argument('-d', '--accumulation',
                        default = r'/datasets/projects-hydrology/routomator/data/input/flow-acc-15.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-c', '--catchment',
                        default = r'/datasets/projects-hydrology/routomator/data/tempfiles/test_ws.asc',
                        help = 'Precomputed catchment raster')
    parser.add_argument('-w', '--watershed',
                        default = None, required=True,
                        help = 'Watershed being processed.  Necessary to determine output folder')

    parser.add_argument('-t', '--tempdir',
                        default = r'/datasets/projects-hydrology/routomator/data/tempfiles',
                        help = 'Directory to store intermediate files, must have write permissions')
    parser.add_argument('-o', '--outdir',
                        default = r'/datasets/projects-hydrology/routomator/data/output',
                        help = 'Directory to store output files, must have write permissions')

    args = parser.parse_args()
    main(args)
