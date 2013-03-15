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

# Subset to desired subwatersheds

# sub <- cwb.ogr[cwb.ogr$WTRSHDGRPC=='REVL',]
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

