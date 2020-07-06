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
    call(polygonize)

    acc_cut = ['gdalwarp', '-cutline', ws_shape, args.accumulation, os.path.join(args.output, 'direction.asc')]
    call(acc_cut)
    exit()
        
    from rpy2.robjects import r
    raster = importr('raster')
    rgdal = importr('rgdal')

    print('Loading Catchement Raster')
    catch = raster.raster(args.catchment)

    print('Clipping accumulation raster to watershed area')
    acc = raster.raster(acc)
    acc_masked = raster.mask(acc, catch)
    r.assign('acc_masked', acc_masked)
    r('acc_masked[is.na(acc_masked)] <- -9999')
    raster.NAvalue(acc_masked) = -9999

    print('Saving clipped accumulation file')
    raster.writeRaster(acc_masked, filename=os.path.join(tempdir, 'acc_masked.asc'), format='ascii', overwrite=True, NAFlag=-9999)

    print('Selecting stations in watershed area')
    hydat = r'/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat_gt_500km2_catch_wgs84.shp'
    d = os.path.dirname(args.hydat)
    f = os.path.splitext(os.path.basename(args.hydat))[0]
    hydat = rgdal.readOGR(d, f, stringsAsFactors=False)
    r.assign('hydat', hydat)
    watershed_poly = raster.rasterToPolygons(catch)
    r.assign('watershed_poly', watershed_poly)
    
    sp = importr('sp')
    station = sp.over(watershed_poly, hydat)

    # correct invalid edge flows
    correct_edge_flows(r)
    print('Invalid Directions Fixed')
    outfile = os.path.join(args.outdir, args.watershed, 'flow_vic.asc')
    r.change_nodata('-9999')
    r.save(outfile)

    # Load as direction raster
    r = DirectionRaster(outfile)
    r.save_arcgis(os.path.join(args.outdir, args.watershed, 'flow_arcgis.asc'))
    print('Loading Stations')
    stns = load_stations(args.stations)
    stns = generate_shortnames(stns)

    print('Generating Subbasin Masks')
    generate_subbasin_masks(stns, r, os.path.join(args.outdir, args.watershed))

    print('Done generating masks')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Routomator master script')

    parser.add_argument('-d', '--direction',
                        default = r'/datasets/projects-hydrology/routomator/data/input/flow-dir-15.asc',
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
