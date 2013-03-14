library(maptools)
library(sp)
library(raster)
library(rgdal)
library(rgeos)

#~ source("data_sources.r")
# Sources file paths for:dem, cwb, extent_shapefile, hydat, veg
# a header character string for output
# and raster object for: extent_raster


plot.grass <- function(layer, type) {
    if (type == 'raster') {
        temp <- readRAST6(layer)
        image(temp)
    }
    else {
        temp <- readVECT6(layer)
        plot(temp)
    }
}

#~ dem <- "/home/bveerman/Windy/data/gis/basedata/DEMS/SRTM_DEM/SRTM_CSI_CGIAR_v3/z_frsrg_3as.txt"
dem <- "/home/data/gis/basedata/DEMS/SRTM_DEM/SRTM_CSI_CGIAR_v4_1/srtm_bc_buffered.tif"

#~ cwb <- "/home/bveerman/Windy/data/gis/basedata/BC_Water/BC_CWB/CWB_WS_GRP/CWB_WS_GRP_wgs1984.shp"
cwb <- "/home/data/gis/basedata/BC_Water/BC_CWB/CWB_WS_GRP/CWB_WS_GRP_wgs1984.shp"

extent_shapefile <- "/home/data/gis/vic_final_columbia/col_net3_pjl.shp"

hydat <- "/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat.shp"


#~ out.path <- "/home/bveerman/Windy/bveerman/hydrology/vic_routing/rout_output"
out.path <- "/home/bveerman/hydrology/vic_routing/rout_output"


# basic extent raster to be used for all files
ext = extent(-139, -114, 47, 61)
extent_raster <- raster(nrows=224, ncols=400, ext=ext)

header <- 'ncols         400
nrows         224
xllcorner     -139
yllcorner     47
cellsize      0.0625
NODATA_value  0
'

####################################
##### Preprocess Watersheds  #######
####################################

## load cwb polys and subset to selected watersheds
subbasins = c('REVL','SIML','CANO','OKAN','KOTR','LARL','BULL','KETL',
        'SMAR','KOTL','KHOR','DUNC','UARL','SLOC','CLRH','ELKR','COLR')

d <- dirname(cwb)
f <- sub("\\.[^.]*$", "", basename(cwb))

cwb.ogr <- readOGR(d, f, stringsAsFactors = FALSE)

## Subset to desired subwatersheds

#~ sub <- cwb.ogr[cwb.ogr$WTRSHDGRPC=='REVL',]
watersheds <- cwb.ogr[cwb.ogr$WTRSHDGRPC %in% subbasins,]
watersheds_merged <- unionSpatialPolygons(watersheds, ID=rep(1,time=length(watersheds@polygons)))

## Open province layer to clip any anything else to before processing

d <- dirname(extent_shapefile)
f <- sub("\\.[^.]*$", "", basename(extent_shapefile))

extent.shp <- readOGR(d, f, stringsAsFactors = FALSE)

Fraction file define determination of subbasins

####################################
##### Create Fraction Raster #######
####################################

fraction <- rasterize(watersheds_merged, extent_raster, getCover=TRUE)
writeRaster(fraction, filename=file.path(out.path, 'fraction.asc'), overwrite=TRUE, NAflag=0)

#####################################
##### Create Direction Raster #######
#####################################

#~ The flow direction file tells the routing model how all of the grid 
#~ cells are connected in the routing net. The format is an arc/info ascii 
#~ grid. It contains a 6-line header that tells the routing model the lower 
#~ left latitude and longitude, the number of rows and columns, and the 
#~ grid cell resolution.

library(spgrass6)

watershed <- 'columbia'
subbasins <- c('REVL','SIML','CANO','OKAN','KOTR','LARL','BULL','KETL','SMAR','KOTL','KHOR','DUNC','UARL','SLOC','CLRH','ELKR','COLR')

#~ watershed <- 'peace'
#~ subbasins <- c('AKIEC','BCPCN','GRAHM','HALGR','KWADA','MOBER','MURWV','NATMO','OSILI','PACKM','PEACT','PINPN','BCGMS','FINAK','HALFA','INGEN','MESIL','MURMO','NATFT','OMNOS','OSPIK','PARMS','PEAPN','SUKMO')

# Load in existing location
#loc <- initGRASS("/usr/lib/grass64", home='/home/bveerman/', gisDbase='/home/bveerman/grassdata', location='vic_routing', mapset='PERMANENT', override=TRUE)
loc <- initGRASS(gisBase="/home/bveerman/download/grass_trunk/dist.x86_64-unknown-linux-gnu", home='/home/bveerman/', gisDbase='/home/bveerman/grassdata', location='vic_routing', mapset='PERMANENT', override=TRUE)
execGRASS('d.mon', parameters=list(start='wx1'))

# list all mapsets
execGRASS("g.mapsets", flags=c("l"))
# list mapsets in current search path
execGRASS("g.mapsets", flags=c("p"))

# if creating mapset for the first time:
create <- FALSE
if (create == TRUE) {
  execGRASS("g.mapset", flags="c", parameters=list(mapset=watershed, location='vic_routing'))
  execGRASS("g.mapsets", parameters=list(mapset=watershed, operation='add'))
  execGRASS("g.mapsets", parameters=list(mapset='PERMANENT', operation='add'))
  execGRASS("g.mapset", parameters=list(mapset=watershed))
  # create watershed boundary based on subbasin selections
  d <- dirname(cwb)
  f <- sub("\\.[^.]*$", "", basename(cwb))
  query <- paste("WTRSHDGRPC IN ('", paste(subbasins, collapse="', '"), "')", sep='')
  execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, where=query, output="ws"))
} else {
  execGRASS("g.mapsets", parameters=list(mapset=watershed, operation='add'))
  execGRASS("g.mapset", parameters=list(mapset=watershed))
}

# make sure we have all the necessary layers
execGRASS("g.list", flags="f", parameters=list(type='rast'))
execGRASS("g.list", flags="f", parameters=list(type='vect'))


### DEM PREP ###
# mask all raster operations to watershed region
execGRASS("v.db.addcol", parameters=list(map="ws", columns="merge"))
execGRASS("v.category", flags=c('overwrite'), parameters=list(input="ws", output="wstemp", option='del'))
execGRASS("v.category", flags=c('overwrite'), parameters=list(input="ws", output="ws", option='add', cat=as.integer(1), step=as.integer(0)))
execGRASS("v.dissolve", parameters=list(input="wscat", output="wsdissolve"))
execGRASS("v.to.rast", parameters=list(input="ws", output="ws-boundary", type='line', use='val', value=1))
execGRASS("r.mask", parameters=list(vector="ws"))

# METHOD 1: create a filled dem, burn streams, pipe to r.terraflow (r.flow possible as well)
execGRASS("g.region", parameters=list(rast="dem-15"))
execGRASS("r.fill.dir", flags="overwrite", parameters=list(input='dem-15', output="dem-filled-15", outdir="dem-filled-dir-15"))
#execGRASS("r.carve", flags="n", parameters=list(rast="dem-filled-15", vect="stream", output="dem-carved-15")) #takes FOREVER!!!
execGRASS("r.fill.dir", flags="overwrite", parameters=list(input='dem-carved-15', output="dem-filled-carved-15", outdir="dem-filled-carved-dir-15"))
execGRASS("r.terraflow", flags="overwrite", parameters=list(elevation="dem-filled-carved-15", drainage='flow-dir-15', accumulation="flow-accumulation-tf-15"))
          
# METHOD 2: using r.hydrodem with minimal corrections, pipe to r.watershed
execGRASS("g.region", parameters=list(rast="dem-15"))
execGRASS("r.hydrodem", parameters=list(input='dem-15', output="dem-hydrodem-15"))
execGRASS("r.watershed", flags=c("overwrite", "s", "b"), parameters=list(elevation="dem-hydrodem-15", accumulation="flow-accumulation-ws-15", drainage="flow-dir-ws-15"))
# r.watershed uses negative values for flow accumunation values on perimeter, must correct
execGRASS("r.mapcalc", parameters=list(expression="'flow-accumulation-ws-15-abs'=abs('flow-accumulation-ws-15')"))

execGRASS("r.stats", flags=c('p'), parameters=list(input='flow-accumulation-ws-15-abs'))

# EXPORT CONDIDTIONED DEM FOR make_rout.scr
execGRASS("r.out.arc", flags=c("overwrite"), parameters=list(input='flow-accumulation-ws-15-abs', output="flow-acc-15"))


readRAST6(vname, cat=NULL, ignore.stderr = NULL, NODATA=NULL, plugin=NULL, mapset=NULL, useGDAL=NUL

m.sbw1
r.terraflow
r.fill.dir
r.watershed
r.carve

unlink_.gislock()


