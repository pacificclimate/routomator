import os
import argparse

from subprocess import call

import shapefile

from routomator.raster import DirectionRaster
from routomator.station import load_stations, load_stations_w_shortnames, generate_shortnames, generate_single_subbasin_mask, generate_station_file, generate_upstream_station_dict

def main(args):
    # Need to clip the stations by the watershed area, most efficient in gdal
    ws_shape = os.path.join(args.tempdir, 'ws.shp')
    hydat_ws = os.path.join(args.tempdir, 'hydat.csv') 

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

    print 'Generating VIC Subbasin Masks'
    i = 0
    total = len(stns)
    print '{} Stations total'.format(total)
    upstream_stations = generate_upstream_station_dict(stns, r)
    
    headwater_stations = [station for station in stns if station.raster_coords(r) not in upstream_stations.keys()]
    print '{} Headwater stations'.format(len(headwater_stations))
    for station in headwater_stations:
        print '[{}/{}]: {}'.format(i, total, station.long_name)
        i += 1
        temp_raster = r.copy_dummy()
        temp_raster.save(os.path.join(args.outdir, station.short_name + '_subbasin_headwater.asc'))
        del(temp_raster)

    interior_stations = [station for station in stns if station.raster_coords(r) in upstream_stations.keys()]
    print '{} Interior stations'.format(len(interior_stations))
    for station in interior_stations:
        print '[{}/{}]: {}'.format(i, total, station.long_name)
        i += 1
        temp_raster = generate_single_subbasin_mask(upstream_stations[station.raster_coords(r)], r)
        temp_raster.save(os.path.join(args.outdir, station.short_name + '_subbasin_interior.asc'))
        del(temp_raster)
    print 'Done generating VIC Subbasin Masks'

    print 'Generating Diagnostic Output'
    i = 0
    # w = shapefile.Writer()
    for station in stns:
        print '[{}/{}]: {}'.format(i, total, station.long_name)
        
        # Convert to geotiff
        temp_raster = r.catchment_mask(station.raster_coords(r))
        gtif_fn = os.path.join(args.outdir, 'catchment_' + station.short_name + '.tif')
        temp_raster.save_geotiff(gtif_fn)
        del(temp_raster)

        # Copy to shapefile
        shp_fn = os.path.join(args.outdir, 'catchment_' + station.short_name + '.shp')
        polygonize = [
            'gdal_polygonize.py',
            gtif_fn,
            '-f', 'ESRI Shapefile', '-q',
            shp_fn
            ]
        call(polygonize)

    #     # Merge with existing shapefiles
    #     shp_reader = shapefile.Reader(shp_fn)
    #     if len(sf.shapes) > 1:
    #         # Do something...
    #     w._shapes.extend(shp_reader.shapes())
    #     w.records.extend(shp_reader.records())
    #     i += 1

    # # Shapefile busywork
    # w.fields = list(shp_reader.fields)
    # w.save(os.path.join(args.outdir, 'subbasins_merged'))

    print 'Done creating diagnostic output'

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
