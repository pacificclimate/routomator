library(spgrass6)

source('config.r')

# Load in existing location
loc <- initGRASS(gisBase=gisBase, home='/home/bveerman/', gisDbase=gisDbase, location=location, mapset='PERMANENT', override=TRUE)

# load DEM

execGRASS("r.in.gdal", flags=c('o','overwrite'), parameters=list(input=dem, output="dem"))
execGRASS("g.region", parameters=list(rast="dem"))
execGRASS("r.info", parameters=list(map="dem"))

# make sure hydrodem extension installed
execGRASS('g.extension', flags=c('a', 's'), parameters=list(extension='r.hydrodem'))

# import hydat
d <- dirname(hydat)
f <- sub("\\.[^.]*$", "", basename(hydat))
execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, output="hydat"))

# list whats been imported so far
execGRASS("g.list", flags="f", parameters=list(type='rast'))
execGRASS("g.list", flags="f", parameters=list(type='vect'))

