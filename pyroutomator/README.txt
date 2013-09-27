Installing the package

1) Clone/extract the pacakge to a local directory
2) Install using the included setup script (python setup.py install, or python setup.py install --user if you don't have system permissions)

Running the Scripts

All of the python scripts have built in help.  This can be shown by using the command line option -h/--help, for "example generate_ws_catch.py -h"

Made temporary and output directories and bind them to environment variables:
$ mkdir /datasets/projects-hydrology/routomator/data/testrun
$ mkdir /datasets/projects-hydrology/routomator/data/testrun/tempfiles
$ mkdir /datasets/projects-hydrology/routomator/data/testrun/output

$ TEMPDIR=/datasets/projects-hydrology/routomator/data/testrun/tempfiles
$ OUTDIR=/datasets/projects-hydrology/routomator/data/testrun/output

generate_ws_catch.py -d /datasets/projects-hydrology/routomator/data/input/flow-dir-15.asc -l 49.2270,-121.8400 -t $TEMPDIR

generate_fraction_file.py -c $TEMPDIR/ws.asc -o $OUTDIR

generate_vel_diff_file.py -f $OUTDIR/fraction.asc -o $OUTDIR -v /home/data/gis/vic_bc/vegetation/majority1km2_wgs84_gen2_extent.shp

prep_accumulation.py -a /datasets/projects-hydrology/routomator/data/input/flow-acc-15.asc -c $TEMPDIR/ws.asc -o $OUTDIR -t $TEMPDIR

Go into {routomator package dir}/flowgen
run 'make' to make the flowgen/convert binaries
Then:
./make_rout.sh $TEMPDIR/accumulation_clipped.asc $OUTDIR/direction.asc

generate_xmask.py -d $OUTDIR/direction.asc -o $OUTDIR

generate_stations_subbasins.py -d $OUTDIR/direction.asc -c $TEMPDIR/ws.asc -s "/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat_gt_500km2_catch_wgs84.shp" -o $OUTDIR -t $TEMPDIR --overwrite

