import os
import argparse

from .raster import AsciiRaster
from routomator.direction import correct_edge_flows




def main(args):
    if args.watershed is None: assert 'Watershed argument missing'

    r = AsciiRaster(args.input)
    
    # find all invalid values
    correct_edge_flows(r)
 
    print 'Invalid Directions Fixed'

    outfile = os.path.join(args.outdir, args.watershed, 'flow-dir-16th-corrected.asc')
    r.save(outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flow direction corrector')
    parser.add_argument('-i', '--input',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/tempfiles/flow-dir-16th.asc',
                        help = 'Input direction ascii raster')
    parser.add_argument('-w', '--watershed',
                        default = None,
                        help = 'Watershed being processed.  Necessary to determine output folder')
    parser.add_argument('-o', '--outdir',
                        default = r'/home/data/projects/hydrology/vic/data/routomator/output',
                        help = 'Output direction corrected ascii raster')
    parser.add_argument('-v', '--verbose',
                        default = False, action='store_true',
                        help = 'Show additional progress information')
    args = parser.parse_args()
    main(args)
