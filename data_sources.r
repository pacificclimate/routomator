dem <- "/home/data/gis/basedata/DEMS/SRTM_DEM/SRTM_CSI_CGIAR_v3/z_frsrg_3as.txt"
cwb <- "/home/data/gis/basedata/BC_Water/BC_CWB/CWB_WS_GRP/CWB_WS_GRP_wgs1984.shp"
extent_shapefile <- "/home/data/gis/vic_final_columbia/col_net3_pjl.shp"
hydat <- "/home/data/gis/basedata/HYDAT_STN/Canada Hydat/canada_hydat.shp"
veg <- "/home/data/gis/vic_bc/vegetation/majority1km2.shp"
out.path <- "/home/bveerman/vic_routing/rout_output"


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
