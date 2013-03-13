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


# add watershed specific mapset if doesn't already exist
execGRASS("g.mapsets", flags=c("l","p"))

execGRASS("g.mapsets", parameters=list(removemapset=watershed))

execGRASS("g.mapset", flags="c", parameters=list(mapset=watershed, location='vic_routing'))
execGRASS("g.mapsets", parameters=list(addmapset=watershed))
execGRASS("g.mapsets", parameters=list(addmapset='PERMANENT'))
execGRASS("g.mapset", parameters=list(mapset=watershed))
execGRASS("g.region", parameters=list(rast="dem-15"))

# make sure we have all the necessary layers
execGRASS("g.list", flags="f", parameters=list(type='rast'))
execGRASS("g.list", flags="f", parameters=list(type='vect'))

# create watershed boundary based on subbasin selections
d <- dirname(cwb)
f <- sub("\\.[^.]*$", "", basename(cwb))
query <- paste("WTRSHDGRPC IN ('", paste(subbasins, collapse="', '"), "')", sep='')
execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, where=query, output="ws"))

# should we mask to watershed region?
# http://lists.osgeo.org/pipermail/grass-user/2010-September/057962.html

# create a filled direction raster
execGRASS("g.region", parameters=list(rast="dem-15"))
execGRASS("r.fill.dir", flags="overwrite", parameters=list(input='dem-15', elevation="dem-filled-15", direction="dem-direction-15"))
execGRASS('d.rast', parameters=list(map="dem-direction-15"))


# from filled direction raster, burn in streams and re-fill
execGRASS("r.carve", flags="n", parameters=list(rast="dem-filled-15", vect="stream", output="dem-carved-15"))
# currently takes forever.... lets check output map w/out burning first
#~ execGRASS("r.fill.dir", flags="overwrite", parameters=list(input='dem-carved-15', elevation="dem-final-15"))

# final 15as DEM is now used to creat flow direction and accumulation
execGRASS("g.remove", parameters=list(rast="flow-accumulation-15"))
execGRASS("g.remove", parameters=list(rast="flow-dir-15"))
execGRASS("r.watershed", flags="overwrite", parameters=list(elevation="dem-filled-15", drainage='flow-dir-15', accumulation="flow-accumulation-15"))

execGRASS('d.mon', parameters=list(start='x0'))

readRAST6(vname, cat=NULL, ignore.stderr = NULL, NODATA=NULL, plugin=NULL, mapset=NULL, useGDAL=NUL

m.sbw1
r.terraflow
r.fill.dir
r.watershed
r.carve

unlink_.gislock()


