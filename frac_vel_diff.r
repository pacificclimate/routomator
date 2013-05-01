library(maptools)
library(sp)
library(raster)
library(rgdal)
library(rgeos)

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

# basic extent raster to be used for all files
ext = extent(-139, -114, 47, 61)
extent_raster <- raster(nrows=224, ncols=400, ext=ext)

####################################
##### Preprocess Watersheds  #######
####################################

source('config.r')

d <- dirname(cwb)
f <- sub("\\.[^.]*$", "", basename(cwb))

cwb.ogr <- readOGR(d, f, stringsAsFactors = FALSE)

# Subset to desired subwatersheds

# sub <- cwb.ogr[cwb.ogr$WTRSHDGRPC=='REVL',]
watersheds <- cwb.ogr[cwb.ogr$WTRSHDGRPC %in% subbasins,]
watersheds_merged <- unionSpatialPolygons(watersheds, ID=rep(1,time=length(watersheds@polygons)))


####################################
##### Create Fraction Raster #######
####################################

fraction <- rasterize(watersheds_merged, extent_raster, getCover=TRUE)
writeRaster(fraction, filename=file.path(outdir, 'fraction.asc'), overwrite=TRUE, NAflag=0)

####################################
##### Create Velocity Raster #######
####################################

#~ Flow Velocity File – an ASCII file generated in ArcGIS that defines 
#~ the velocity of flow withqmajority of the cell. Cells with lakes are 
#~ identified using the vegetation layer used in VIC. 
#~ /home/data/projects/hydrology/vic/data/columbia_cc_rout/vel_ccolu_0625dd.txt

library(rgdal)
library(raster)

# create a velocity raster assuming all cells in watershed are rivers
velocity.raster <- fraction
velocity.raster[which(velocity.raster[]>0)] <- 2

# find lakes using veg shapefile
d <- dirname(veg)
f <- sub("\\.[^.]*$", "", basename(veg))

threshold <- 50
veg.shape <- readOGR(d, f, stringsAsFactors = FALSE)
veg.shape.lakes <- veg.shape[veg.shape$GRIDCODE==20,]
lakes.raster <- rasterize(veg.shape.lakes, extent_raster, getCover=TRUE)

# subset lakes raster to watershed
lakes.raster[which(fraction[]==0)] <- 0

# now insert lake positions
velocity.raster[which(lakes.raster[]>threshold)] <- 0.3

# write out..
writeRaster(velocity.raster, filename=file.path(outdir, 'velocity.asc'), overwrite=TRUE, NAflag=0)

#####################################
##### Create Diffusion Raster #######
#####################################

#~ Flow Diffusion File – an ASCII file generated in ArcGIS that defines 
#~ the diffusion of flow within each cell, the standard value is 2000, 1300 
#~ is used where lakes cover a majority of the cell.
#~ /home/data/projects/hydrology/vic/data/columbia_cc_rout/diff_ccolu_0625dd.txt
#~ Go to this external document for details on how to create the flow 
#~ velocity and diffusion files: 
#~ W:\Projects\VIC\MANUAL\BCH_Peace_Campbell_Columbia\Routing\Creating_Inputs\2_Vel_Diff-1.0.docx

# This can be created simply by recalculating the velocity raster...

diffusion.raster <- velocity.raster
diffusion.raster[which(diffusion.raster[]==2)] <- 2000
diffusion.raster[which(diffusion.raster[]==0.3)] <- 1300

# write out..
writeRaster(diffusion.raster, filename=file.path(outdir, 'diffusion.asc'), overwrite=TRUE, NAflag=0)

