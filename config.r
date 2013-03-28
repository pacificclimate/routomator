# This is the config file to set parameters before running the associated parts.
# Any neccessary options must be here

outdir <- '.'
verbose <- TRUE
method = 2 #choose method 1 or 2 for creating flow accumulation raster for flowgen.c
# What watershed are we calculating for?
watershed <- 'columbia'
subbasins <- c('REVL','SIML','CANO','OKAN','KOTR','LARL','BULL','KETL','SMAR','KOTL','KHOR','DUNC','UARL','SLOC','CLRH','ELKR','COLR')
watershed.isnew <- FALSE

#~ watershed <- 'peace'
#~ subbasins <- c('AKIEC','BCPCN','GRAHM','HALGR','KWADA','MOBER','MURWV','NATMO','OSILI','PACKM','PEACT','PINPN','BCGMS','FINAK','HALFA','INGEN','MESIL','MURMO','NATFT','OMNOS','OSPIK','PARMS','PEAPN','SUKMO')

# GRASS7 settings
gisBase <- "/home/bveerman/download/grass_trunk/dist.x86_64-unknown-linux-gnu"
gisDbase <- '/home/bveerman/grassdata'
location <- 'vic_routing'
