# This is the config file to set parameters before running the associated parts.
# Any neccessary options must be here



# What watershed are we calculating for?
watershed <- 'peace'

## watershed <- 'peace'
## subbasins <- c('AKIEC','BCPCN','GRAHM','HALGR','KWADA','MOBER','MURWV','NATMO','OSILI','PACKM','PEACT','PINPN','BCGMS','FINAK','HALFA','INGEN','MESIL','MURMO','NATFT','OMNOS','OSPIK','PARMS','PEAPN','SUKMO')

outdir <- file.path('/home/data/projects/hydrology/vic/data/routomator/output', watershed)
dir.create(outdir)
tempfiles <- '/home/data/projects/hydrology/vic/data/routomator/tempfiles'
verbose <- TRUE

# GRASS7 settings - You should not need to change these unless on a different machine or something

veg <- "/home/data/gis/vic_bc/vegetation/majority1km2_wgs84_BC.shp"
gisBase <- "/home/data/projects/comp_support/software/grass7_trunk/dist.x86_64-unknown-linux-gnu"
gisDbase <- '/home/data/projects/hydrology/vic/data/routomator/grassdata'
location <- 'test6'