import os
import argparse

from rpy2.robjects import r
from rpy2.robjects.packages import importr

def main(args):
    from rpy2.robjects import r
    raster = importr('raster')
    rgdal = importr('rgdal')

    print 'Loading Catchement Raster'
    fraction = raster.raster(args.fraction)
    r.assign('fraction', fraction)

    # Calculate Velocity Raster
    print 'Calculating Velocity Layer'
    threshold = 30
    velocity = fraction
    r.assign('velocity', velocity)
    r('velocity[which(velocity[]>0)] <- 2')

    print '\tLoading Vegetation Layer'
    d = os.path.dirname(args.vegetation)
    f = os.path.splitext(os.path.basename(args.vegetation))[0]
    veg_shape = rgdal.readOGR(d, f, stringsAsFactors=False)
    r.assign('veg_shape', veg_shape)
    lakes = r('veg_shape[veg_shape$GRIDCODE==20,]')
    lakes_raster = raster.rasterize(lakes, fraction, getCover=True)

    print '\tTransforming lakes layer into raster coordinates'
    r.assign('lakes_raster', lakes_raster)
    r('lakes_raster[which(is.na(fraction[]))] <- 0')
    r.assign('threshold', threshold)
    r('velocity[which(lakes_raster[]>threshold)] <- 0.3')
    velocity = r('velocity')

    print '\tSaving Velocity Layer'
    raster.writeRaster(velocity, filename=os.path.join(args.outdir, 'velocity.asc'), format='ascii', overwrite=True, NAflag=0)

    # Create Diffusion Raster #######
    print '\tCreating Diffusion File'
    r('diffusion <- velocity')
    r('diffusion[which(diffusion[]==2)] <- 2000')
    r('diffusion[which(diffusion[]==0.3)] <- 1300')
    print '\tSaving Diffusion File'
    diffusion = r('diffusion')
    raster.writeRaster(diffusion, filename=os.path.join(args.outdir, 'diffusion.asc'), format='ascii', overwrite=True, NAflag=0)
    print '\tDone saving diffusion file'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Velocity and diffusion raster generator')

    parser.add_argument('-f', '--fraction',
                        default = r'/datasets/projects-hydrology/routomator/data/output/fraction.asc',
                        help = 'Precomputed fraction raster')
    parser.add_argument('-v', '--vegetation',
                        default = r'/home/data/gis/vic_bc/vegetation/majority1km2_wgs84_gen2_extent.shp',
                        help = 'Shapefile containing vegation layer')
    parser.add_argument('-o', '--outdir',
                        default = r'/datasets/projects-hydrology/routomator/data/output',
                        help = 'Directory to store output files, must have write permissions')
    args = parser.parse_args()
    main(args)
