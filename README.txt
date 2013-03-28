VIC Routomator 

Version:0.1b
Author: Basil Veerman

Overview:
The Vic Routomator is designed to automate the creation of input files require for the VIC routing model.

Requirements:
GRASS7.0-svn
R with modules:sp, maptools, raster, xml, rgdal, rgeos, spgrass6

Raster files that are produced:
Flow Direction in VIC format directions:
     8  1  2
     7  x  3
     6  5  4
Flow Accumulation
Flow Velocity
Flow Diffusion
Subbasin Masks
Xmask

All raster files are have 16th degree resolution in WGS84 coordinates using a standard header.

ncols 400
nrows 224
xllcorner -139
yllcorner 47
cellsize 0.0625
NODATA_value 0
*note NODATA_value default is -9999 in Arc

Additional files created is a station location file that identifies the grid cell number a valid station is located in.

All configuration options are detailed in config.r.

1). Must first run 'make all' to compile the flowgen and conver binaries.
2). Scripts can be run individually in order: grass_prep.r, direction.r, fraction.r, velocity_diffusion.r, xmask.py
