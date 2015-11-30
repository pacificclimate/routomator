import os
import argparse

from subprocess import call

import shapefile

from routomator.raster import DirectionRaster
from routomator.station import load_stations, load_stations_w_shortnames, generate_shortnames, generate_single_subbasin_mask, generate_station_file, generate_upstream_station_dict

def main(args):

    hydat_ws = os.path.join(args.tempdir, 'hydat.csv')

    stns = load_stations(hydat_ws)
    stns = generate_shortnames(stns)

    print 'Generating Station File'
    s = generate_station_map(stns, r)
    stn_fp = os.path.join(args.outdir, 'station_map.txt')
    with open(stn_fp, 'wb') as f:
        f.write(s)
    print 'Done generating station map'
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Subbasin and station file generator')

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
