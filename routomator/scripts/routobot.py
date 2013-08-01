import os
import argparse

from routomator.raster import AsciiRaster, DirectionRaster
from routomator.direction import correct_edge_flows
from routomator.station import load_stations, generate_shortnames, generate_subbasin_masks

def main(args):
    if args.watershed is None: assert 'Watershed argument missing'

    r = AsciiRaster(args.input)
    
    # correct invalid edge flows
    correct_edge_flows(r)
    print 'Invalid Directions Fixed'
    outfile = os.path.join(args.outdir, args.watershed, 'flow_vic.asc')
    r.change_nodata('-9999')
    r.save(outfile)

    # Load as direction raster
    r = DirectionRaster(outfile)
    r.save_arcgis(os.path.join(args.outdir, args.watershed, 'flow_arcgis.asc'))
    print 'Loading Stations'
    stns = load_stations(args.stations)
    stns = generate_shortnames(stns)

    print 'Generating Subbasin Masks'
    generate_subbasin_masks(stns, r, os.path.join(args.outdir, args.watershed))

    print 'Done generating masks'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Routomator master script')
    parser.add_argument('-i', '--input',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/tempfiles/flow-dir-16th.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-w', '--watershed',
                        default = None,
                        help = 'Watershed being processed.  Necessary to determine output folder')
    parser.add_argument('-s', '--stations',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/tempfiles/hydat_ws.csv',
                        help = 'Stations within watershed boundary, csv file')    
    parser.add_argument('-o', '--outdir',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/output',
                        help = 'Output direction corrected ascii raster')
    parser.add_argument('-v', '--verbose',
                        default = False, action='store_true',
                        help = 'Show additional progress information')
    args = parser.parse_args()
    main(args)