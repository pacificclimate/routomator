library(spgrass6)

source('config.r')


# Load in existing location
loc <- initGRASS(gisBase=gisBase, home='/home/bveerman/', gisDbase=gisDbase, location=location, mapset='PERMANENT', override=TRUE)

# load DEM
dem <- "/home/data/gis/basedata/DEMS/SRTM_DEM/SRTM_CSI_CGIAR_v4_1/srtm_bc_buffered.tif"
execGRASS("r.in.gdal", flags=c('o','overwrite'), parameters=list(input=dem, output="dem"))
execGRASS("g.region", parameters=list(rast="dem"))
execGRASS("r.info", parameters=list(map="dem"))

# aggregate DEM to 15as
execGRASS("g.region", parameters=list(w='-139', s='47', n='61', e='-114', nsres='0.004166667', ewres='0.004166667'))
execGRASS("r.resamp.stats", parameters=list(input='dem', output= 'dem-15'))

# pull in region information from raster
#execGRASS("g.region", flags='l')
#execGRASS("g.region", parameters=list(rast="dem"))

# make sure hydrodem extension installed
execGRASS('g.extension', flags=c('a', 's'), parameters=list(extension='r.hydrodem'))

# import watersheds
cwb <- "/home/data/gis/basedata/BC_Water/BC_CWB/CWB_WS_GRP/CWB_WS_GRP_wgs1984.shp"
d <- dirname(cwb)
f <- sub("\\.[^.]*$", "", basename(cwb))
execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, output="cwb"))

# import streams
stream <- "/home/data/gis/basedata/BC_Water/BC_CWB/CWB_STRM_N/bc_cwb_streams_order_6_and_greater_WGS84.shp"
d <- dirname(stream)
f <- sub("\\.[^.]*$", "", basename(stream))
execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, output="stream"))

# import hydat
hydat <- "/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat_gt_500km2_catch_wgs84.shp"
d <- dirname(hydat)
f <- sub("\\.[^.]*$", "", basename(hydat))
execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, output="hydat"))

# list whats been imported so far
execGRASS("g.list", flags="f", parameters=list(type='rast'))
execGRASS("g.list", flags="f", parameters=list(type='vect'))
