library(spgrass6)

dem <- "/home/data/gis/basedata/DEMS/SRTM_DEM/SRTM_CSI_CGIAR_v4_1/srtm_bc_buffered.tif"
cwb <- "/home/data/gis/basedata/BC_Water/BC_CWB/CWB_WS_GRP/CWB_WS_GRP_wgs1984.shp"
hydat <- "/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat.shp"
out.path <- "/home/bveerman/hydrology/vic_routing/rout_output"

# Load in existing location
loc <- initGRASS("/usr/lib/grass64", override=TRUE, home='/home/bveerman/', gisDbase='/home/bveerman/grassdata', location='vic_routing', mapset='PERMANENT')
execGRASS("g.mapset", parameters=list(mapset="PERMANENT"))

# load DEM
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
execGRASS("g.region", parameters=list(nsres='0.0041665', ewres='0.0041665'))

g.region w=139:00:00W s=47:00:00N n=61:00:00N e=114:00:00W cols=400 rows=224 nsres=00:03:45 ewres=00:03:45

stream <- "/home/data/gis/basedata/BC_Water/BC_CWB/CWB_STRM_N/bc_cwb_streams_order_6_and_greater_WGS84.shp"
d <- dirname(stream)
f <- sub("\\.[^.]*$", "", basename(stream))
execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, output="stream"))


execGRASS("g.list", flags="f", parameters=list(type='rast'))
execGRASS("g.list", flags="f", parameters=list(type='vect'))
