import os
import argparse
import sys

from subprocess import call

from routomator.raster import DirectionRaster
from routomator.station import load_stations, load_stations_w_shortnames, generate_shortnames, generate_subbasin_masks, generate_station_file

def main(args):
    sys.setrecursionlimit(10000)

    # Need to clip the stations by the watershed area, most efficient in gdal
    ws_shape = os.path.join(args.tempdir, 'ws.shp')
    hydat_ws = os.path.join(args.tempdir, 'hydat.csv') 

    # Load as direction raster
    print 'Loading direction raster'
    r = DirectionRaster(args.direction)
    print 'Loading Stations'

    if args.shortnames:
        stns = load_stations_w_shortnames(hydat_ws)
    else:
        stns = load_stations(hydat_ws)
        stns = generate_shortnames(stns)

    print 'Generating Station Catchment geotiff and shapefiles'
    for station in stns:
        print station.long_name
        temp_raster = r.catchment_mask(station.raster_coords(r))
        gtif_fn = os.path.join(args.outdir, 'catchment_' + station.stn_id + '.tif')
        temp_raster.save_geotiff(gtif_fn)
        del(temp_raster)
        shp_fn = os.path.join(args.outdir, 'catchment_' + station.stn_id + '.shp')
        polygonize = [
            'gdal_polygonize.py',
            gtif_fn,
            '-f', 'ESRI Shapefile',
            shp_fn
            ]
        call(polygonize)
    print 'Done generating station catchments'

    print 'Generating Station File'
    s = generate_station_file(stns, r)
    stn_fp = os.path.join(args.outdir, 'station_file.txt')
    with open(stn_fp, 'wb') as f:
        f.write(s)
    print 'Done generating station file'
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Subbasin and station file generator')

    parser.add_argument('-d', '--direction',
                        default = r'/datasets/projects-hydrology/routomator/data/output/direction.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-c', '--catchment', required=True,
                        help = 'Precomputed catchment raster')
    parser.add_argument('-t', '--tempdir',
                        default = r'/datasets/projects-hydrology/routomator/data/tempfiles',
                        help = 'Directory to store intermediate files, must have write permissions')
    parser.add_argument('-o', '--outdir',
                        default = r'/datasets/projects-hydrology/routomator/data/output',
                        help = 'Directory to store output files, must have write permissions')
    parser.add_argument('--shortnames', action='store_true',
                        default = False,
                        help = 'If the hydat.csv file already has a SHORTNAME field to use for station shortnames')

    args = parser.parse_args()
    main(args)
