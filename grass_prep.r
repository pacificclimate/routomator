library(spgrass6)

# Load in existing location
# grass64
#loc <- initGRASS("/usr/lib/grass64", override=TRUE, home='/home/bveerman/', gisDbase='/home/bveerman/grassdata', location='vic_routing', mapset='PERMANENT')
execGRASS("g.mapset", parameters=list(mapset="PERMANENT"))
# grass7
loc <- initGRASS(gisBase="/home/bveerman/download/grass_trunk/dist.x86_64-unknown-linux-gnu", home='/home/bveerman/', gisDbase='/home/bveerman/grassdata', location='vic_routing', mapset='PERMANENT', override=TRUE)


# load DEM
dem <- "/home/data/gis/basedata/DEMS/SRTM_DEM/SRTM_CSI_CGIAR_v4_1/srtm_bc_buffered.tif"
execGRASS("r.in.gdal", flags=c('o','overwrite'), parameters=list(input=dem, output="dem"))
execGRASS("g.region", parameters=list(rast="dem"))
execGRASS("r.info", parameters=list(map="dem"))

# aggregate DEM to 15as
execGRASS("g.region", parameters=list(res='00:00:15'))
execGRASS("r.resamp.stats", parameters=list(input='dem', output= 'dem-15'))

# pull in region information from raster
execGRASS("g.region", flags='l')
execGRASS("g.region", parameters=list(rast="dem"))

# set up region to aggregate raster into
execGRASS("g.region", parameters=list(w='139:00:00W', s='47:00:00N', n='61:00:00N', e='114:00:00W', nsres='00:03:45', ewres='00:03:45'))
execGRASS("g.region", parameters=list(w='139:00:00W', s='47:00:00N', n='61:00:00N', e='114:00:00W', nsres='00:00:15', ewres='00:00:15'))


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
hydat <- "/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat.shp"
d <- dirname(hydat)
f <- sub("\\.[^.]*$", "", basename(hydat))
execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, output="hydat"))

# list whats been imported so far
execGRASS("g.list", flags="f", parameters=list(type='rast'))
execGRASS("g.list", flags="f", parameters=list(type='vect'))
