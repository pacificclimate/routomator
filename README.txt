Example Routing commands

python generate_ws_catch.py -d FLOW_DIRECTION_ASCII -l LAT,LONG -w WATERSHED_NAME -t TEMPORARY_DIRECTORY
python generate_ws_catch.py -d /datasets/projects-hydrology/routomator/data/input/flow-dir-15.asc -l 49.2270,-121.8400 -w test -t /datasets/projects-hydrology/routomator/data/tempfiles

python generate_fraction_file.py -c CATCHMENT_AREA -w WATERSHED_NAME -o OUTPUT_DIR
python generate_fraction_file.py -c /datasets/projects-hydrology/routomator/data/tempfiles/ws.asc -w test -o /datasets/projects-hydrology/routomator/data/output

python generate_vel_diff_file.py -f FRACTION_FILE -w WATERSHED_NAME -o OUTPUT_DIR -v VEGETATION_FILE
python generate_vel_diff_file.py -f /datasets/projects-hydrology/routomator/data/output/fraction.asc -w test -o /datasets/projects-hydrology/routomator/data/output -v /home/data/gis/vic_bc/vegetation/majority1km2_wgs84_gen2_extent.shp

python prep_accumulation.py -a ACCUMULATION_FILE -c CATCHMENT_AREA -w WATERSHED_NAME -o OUTPUT_DIR -t TEMPORARY_DIRECTORY
python prep_accumulation.py -a /datasets/projects-hydrology/routomator/data/input/flow-acc-15.asc -c /datasets/projects-hydrology/routomator/data/tempfiles/ws.asc -w test -o /datasets/projects-hydrology/routomator/data/output -t /datasets/projects-hydrology/routomator/data/tempfiles

make_rout.sh PREPPED_ACCUMULATION OUTPUT_FLOW_DIR_16TH.asc
make_rout.sh /datasets/projects-hydrology/routomator/data/tempfiles/accumulation_clipped.asc /datasets/projects-hydrology/routomator/data/output/direction.asc

python generate_stations_subbasins.py -c CATCHMENT_AREA -w WATERSHED_NAME -o OUTPUT_DIR -t TEMPORARY_DIRECTORY
python generate_stations_subbasins.py -c /datasets/projects-hydrology/routomator/data/tempfiles/ws.asc -w test -o /datasets/projects-hydrology/routomator/data/output -t /datasets/projects-hydrology/routomator/data/tempfiles
