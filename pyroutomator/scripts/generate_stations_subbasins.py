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
    # Need to clip the stations by the watershed area, most efficient in gdal
    ws_shape = os.path.join(args.tempdir, 'ws.shp')
    hydat_ws = os.path.join(args.tempdir, 'hydat.csv') 
    assert not os.path.exists(hydat_ws), 'File {} already exists, remove it before continuing'.format(hydat_ws)
    clip = ['ogr2ogr', '-overwrite', '-clipsrc', ws_shape, '-f', 'CSV', hydat_ws, args.stations]
    call(clip)

    # Load as direction raster
    r = DirectionRaster(args.direction)
    r.save_arcgis(os.path.join(args.outdir, 'flow_arcgis.asc'))
    print 'Loading Stations'
    stns = load_stations(hydat_ws)
    stns = generate_shortnames(stns)

    print 'Generating Subbasin Masks'
    generate_subbasin_masks(stns, r, args.outdir)
    print 'Done generating masks'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Routomator master script')

    parser.add_argument('-d', '--direction',
                        default = r'/datasets/projects-hydrology/routomator/data/output/direction.asc',
                        help = 'Precomputed catchment raster')
    parser.add_argument('-s', '--stations',
                        default = r'/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat_gt_500km2_catch_wgs84.shp',
                        help = 'Hydat stations shapefile')
    parser.add_argument('-t', '--tempdir',
                        default = r'/datasets/projects-hydrology/routomator/data/tempfiles',
                        help = 'Directory to store intermediate files, must have write permissions')
    parser.add_argument('-o', '--outdir',
                        default = r'/datasets/projects-hydrology/routomator/data/output',
                        help = 'Directory to store output files, must have write permissions')
    args = parser.parse_args()
    main(args)
