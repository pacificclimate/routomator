import math
import argparse
import os

from subprocess import call
from tempfile import NamedTemporaryFile

def main(args):
    xyzpath = os.path.join(args.tempdir, 'direction.csv')
    print 'Converting to XYZ ascii'
    convertascii = [
        'gdal_translate',
        '-of', 'XYZ',
        '-co', 'COLUMN_SEPARATOR=,',
        '-co', 'ADD_HEADER_LINE=YES',
        args.direction,
        xyzpath
        ]
    call(convertascii)
    print 'Done'

    vrt = '''<OGRVRTDataSource>
    <OGRVRTLayer name="{name}">
        <SrcDataSource>{f}</SrcDataSource>
        <GeometryType>wkbPoint</GeometryType>
        <LayerSRS>WGS84</LayerSRS>
        <GeometryField encoding="PointFromColumns" x="X" y="Y"/>
    </OGRVRTLayer>
</OGRVRTDataSource>'''.format(name="direction", f=xyzpath)

    # Save generated VRT as tempfile to load into ogr2ogr
    ### ogr2ogr -overwrite -where "\"Z\" != '0'" output/direction.shp tempfiles/direction.vrt
    vrtpath = os.path.splitext(xyzpath)[0] + '.vrt'
    print vrtpath
    with open(vrtpath, 'wb') as f:
        f.write(vrt)

    convertshp = [
        'ogr2ogr',
        '-overwrite',
        '-select', 'Z',
        '-where', '"Z" != \'0\'',
        os.path.join(args.outdir, 'direction.shp'),
        vrtpath
        ]
    call(convertshp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ascii direction to point converter')
    parser.add_argument('-d', '--direction', required=True,
                        help = 'Input direction ascii raster') 
    parser.add_argument('-t', '--tempdir',
                        help = 'Directory to store intermediate files, must have write permissions')
    parser.add_argument('-o', '--outdir', required=True,
                        help = 'Directory to store output files, must have write permissions')
    args = parser.parse_args()
    main(args)

