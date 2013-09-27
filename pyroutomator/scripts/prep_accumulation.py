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

    print 'Extracting catchment polygon'
    ws_shape = os.path.join(args.tempdir, 'ws.shp')
    polygonize = [
        'gdal_polygonize.py',
        args.catchment,
        '-f', 'ESRI Shapefile',
        ws_shape
        ]
    call(polygonize)

    print 'Clipping accumulation raster to catchment'
    acc_cut = [
        'gdalwarp',
        '-overwrite',
        '-dstnodata', '-9999',
        '-cutline', ws_shape,
        args.accumulation,
        os.path.join(args.tempdir, 'accumulation_clipped.tif')
        ]
    call(acc_cut)

    print 'Saving as Arc Ascii'
    acc_trans = [
        'gdal_translate',
        '-of', 'AAIGrid', os.path.join(args.tempdir, 'accumulation_clipped.tif'),
        os.path.join(args.tempdir, 'accumulation_clipped.asc')
        ]
    call(acc_trans)
    print 'Done'
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Accumulation file prep for flowgen')

    parser.add_argument('-a', '--accumulation',
                        default = r'/datasets/projects-hydrology/routomator/data/input/flow-acc-15.asc',
                        help = 'Input accumulation ascii raster')
    parser.add_argument('-c', '--catchment', required=True,
                        help = 'Precomputed catchment raster')
    parser.add_argument('-t', '--tempdir',
                        default = r'/datasets/projects-hydrology/routomator/data/tempfiles',
                        help = 'Directory to store intermediate files, must have write permissions')
    parser.add_argument('-o', '--outdir',
                        default = r'/datasets/projects-hydrology/routomator/data/output',
                        help = 'Directory to store output files, must have write permissions')

    args = parser.parse_args()
    main(args)
