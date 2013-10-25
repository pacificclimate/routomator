import os
import argparse

from subprocess import call

from routomator.raster import DirectionRaster
from routomator.station import load_stations, load_stations_w_shortnames, generate_shortnames, generate_subbasin_masks

def main(args):
    # Need to clip the stations by the watershed area, most efficient in gdal
    ws_shape = os.path.join(args.tempdir, 'ws.shp')
    hydat_ws = os.path.join(args.tempdir, 'hydat.csv') 

    if os.path.exists(hydat_ws):
        if args.overwrite:
            try:
                os.remove(hydat_ws)
            except:
                raise Exception('Unable to remove hydat file {}, please look into this'.format(hydat_ws))
        else:
            raise Exception('File {} already exists, remove it  or use --overwrite before continuing'.format(hydat_ws))

    print 'Clipping stations to catchment area'
    clip = ['ogr2ogr', '-overwrite', '-clipsrc', ws_shape, '-f', 'CSV', hydat_ws, args.stations]
    call(clip)

    # Load as direction raster
    print 'Loading direction raster'
    r = DirectionRaster(args.direction)
    print 'Saving with ArcGIS direction keys for possible investigation'
    r.save_arcgis(os.path.join(args.outdir, 'flow_arcgis.asc'))
    print 'Loading Stations'

    if args.shortnames:
        stns = load_stations_w_shortnames(hydat_ws)
    else:
        stns = load_stations(hydat_ws)
        stns = generate_shortnames(stns)

    print 'Generating Subbasin Masks'
    generate_subbasin_masks(stns, r, args.outdir)
    print 'Done generating masks'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Subbasin and station file generator')

    parser.add_argument('-d', '--direction',
                        default = r'/datasets/projects-hydrology/routomator/data/output/direction.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-c', '--catchment', required=True,
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
    parser.add_argument('--overwrite', action='store_true',
                        default = False,
                        help = 'If the hydat.csv file already exists in the tempdir, overwrite it')
    parser.add_argument('--shortnames', action='store_true',
                        default = False,
                        help = 'If the hydat.csv file already has a SHORTNAME field to use for station shortnames')

    args = parser.parse_args()
    main(args)
