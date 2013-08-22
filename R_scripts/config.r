# This is the config file to set parameters before running the associated parts.
# Any neccessary options must be here

# GRASS 'location' to create intermediate files in.  This must be set before running grass_prep.r
location <- 'test7'

# What watershed are we calculating for?
# This must correspond to a watershed boundary which has been defined in watershed.r
watershed <- 'peace'

# Specify a base outdir to which the user running the scripts has write permissions
#  -Watershed specific directories will be created as subdirs in this location
outdir <- file.path('/home/data/projects/hydrology/vic/data/routomator/output', watershed)
dir.create(outdir)

# Directory in which to place intermediate outputs
tempfiles <- '/home/data/projects/hydrology/vic/data/routomator/tempfiles'

# DEM layer to use as elevation source
dem <- "/home/data/dem/GMTED2010/15_arcsecond/mn15_nwna.tiff"

# Region wide hydat sites which have previously been filtered.  Will be subsetted to region
hydat <- "/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat_gt_500km2_catch_wgs84.shp"

# Vegetation shapefile that is queried to create the velocity and diffusion files
veg <- "/home/data/gis/vic_bc/vegetation/majority1km2_wgs84_BC.shp"

# TRUE displays a couple extra notification messages...
verbose <- TRUE

# GRASS7 settings - You should not need to change these unless on a different machine or something
gisBase <- "/home/data/projects/comp_support/software/grass7_trunk/dist.x86_64-unknown-linux-gnu" #this is the location of all the grass binaries
gisDbase <- '/home/data/projects/hydrology/vic/data/routomator/grassdata' #head directory for grass to create all locations/watershed
