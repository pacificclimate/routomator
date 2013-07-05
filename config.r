# This is the config file to set parameters before running the associated parts.
# Any neccessary options must be here



# What watershed are we calculating for?
watershed <- 'columbia'
subbasins <- c('REVL','CANO','KOTR','LARL','BULL','SMAR','KOTL','KHOR','DUNC','UARL','SLOC','CLRH','ELKR','COLR')

## watershed <- 'peace'
## subbasins <- c('AKIEC','BCPCN','GRAHM','HALGR','KWADA','MOBER','MURWV','NATMO','OSILI','PACKM','PEACT','PINPN','BCGMS','FINAK','HALFA','INGEN','MESIL','MURMO','NATFT','OMNOS','OSPIK','PARMS','PEAPN','SUKMO')

outdir <- file.path('/home/data/projects/hydrology/vic/data/routomator/output', watershed)
dir.create(outdir)
tempfiles <- '/home/data/projects/hydrology/vic/data/routomator/tempfiles'
verbose <- TRUE
method = 2 #choose method 1 or 2 for creating flow accumulation raster for flowgen.c

# GRASS7 settings - You should not need to change these unless on a different machine or something

veg <- "/home/data/gis/vic_bc/vegetation/majority1km2_wgs84_BC.shp"
cwb <- "/home/data/gis/basedata/BC_Water/BC_CWB/CWB_WS_GRP/CWB_WS_GRP_wgs1984.shp"
stns <- "/home/data/gis/basedata/BC_Water/BC_Hydrometric_Stations/whse_bc_hydrometric_stations_gt_500km2_catch_wgs84.shp"
gisBase <- "/home/data/projects/comp_support/software/grass7_trunk/dist.x86_64-unknown-linux-gnu"
gisDbase <- '/home/data/projects/hydrology/vic/data/routomator/grassdata'
location <- 'vic_routing_test3'
