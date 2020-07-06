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
    from rpy2.robjects import r
    raster = importr('raster')
    rgdal = importr('rgdal')

    # import the previously created watershed area into R
    r('frac_sum <- function(x, ...){sum(x, na.rm=TRUE)/225}')

    print('Loading Catchement Raster')
    catch = raster.raster(args.catchment)
    
    print('Creating Fraction File')
    fraction = raster.aggregate(catch, fact=15, fun=r('frac_sum'))
    r.assign('fraction', fraction)
    print('\tSaving Fraction File')
    raster.writeRaster(fraction, filename=os.path.join(args.outdir, 'fraction.asc'), format='ascii', overwrite=True, NAflag=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Watershed fraction file generator')

    parser.add_argument('-c', '--catchment',
                        default = r'/datasets/projects-hydrology/routomator/data/tempfiles/test_ws.asc',
                        help = 'Precomputed catchment raster')
    parser.add_argument('-o', '--outdir',
                        default = r'/datasets/projects-hydrology/routomator/data/output',
                        help = 'Directory to store output files, must have write permissions')
    args = parser.parse_args()
    main(args)
