# pyroutomator

This is the python part of the routomator and provides scripts to generates watershed catchments, the fraction file, velocity/diffusion files, accumulation files, output xmask, and station subbasins.

## Requirements

1. R library: `module load R`
1. GDAL library and command line tools: `module load gdal`
1. Python version 2. The routomator has not been tested on python 3.

*On current 2016-07-19 compute hardware, you must load R _then_ gdal*

## Installation

Installing the package

```bash
git clone https://github.com/pacificclimate/routomator
cd routomator/pyroutomator
virtualenv -p python2 venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install .
```

## Setup

Make temporary and output directories:

```bash
mkdir /datasets/projects-hydrology/routomator/data/testrun
mkdir /datasets/projects-hydrology/routomator/data/testrun/tempfiles
mkdir /datasets/projects-hydrology/routomator/data/testrun/output
```

For convenience, you can set them to environment variables:

```bash
TEMPDIR=/datasets/projects-hydrology/routomator/data/testrun/tempfiles
OUTDIR=/datasets/projects-hydrology/routomator/data/testrun/output
```

## Running the scripts

All of the python scripts have built in help.  This can be shown by using the command line option -h/--help, for example `generate_ws_catch.py -h`

```bash
generate_ws_catch.py -d /datasets/projects-hydrology/routomator/data/input/flow-dir-15.asc -l 49.2270,-121.8400 -t $TEMPDIR
generate_fraction_file.py -c $TEMPDIR/ws.asc -o $OUTDIR
generate_vel_diff_file.py -f $OUTDIR/fraction.asc -o $OUTDIR -v /home/data/gis/vic_bc/vegetation/majority1km2_wgs84_gen2_extent.shp
prep_accumulation.py -a /datasets/projects-hydrology/routomator/data/input/flow-acc-15.asc -c $TEMPDIR/ws.asc -o $OUTDIR -t $TEMPDIR
```

At this point, some work must be done to convert the 15 arc second accumulation file to a 1/16th degree direction file.

```bash
cd <routomator package dir>/flowgen
make # Generates flogen/conver binaries
./make_rout.sh $TEMPDIR/accumulation_clipped.asc $OUTDIR/direction.asc
```

With the direction raster, proceed to generate the xmask and subbasin files:

```bash
generate_xmask.py -d $OUTDIR/direction.asc -o $OUTDIR
generate_stations_subbasins.py -d $OUTDIR/direction.asc -c $TEMPDIR/ws.asc -s "/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat_gt_500km2_catch_wgs84.shp" -o $OUTDIR -t $TEMPDIR --overwrite
```
