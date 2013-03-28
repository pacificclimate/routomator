#####################################
##### Create Direction Raster #######
#####################################

#~ The flow direction file tells the routing model how all of the grid 
#~ cells are connected in the routing net. The format is an arc/info ascii 
#~ grid. It contains a 6-line header that tells the routing model the lower 
#~ left latitude and longitude, the number of rows and columns, and the 
#~ grid cell resolution.

library(spgrass6)
source('config.r')

# Load in existing location
loc <- initGRASS(gisBase=gisBase, home='/home/bveerman/', gisDbase=gisDbase, location=location, mapset='PERMANENT', override=TRUE)

if (verbose){
  # list all mapsets
  execGRASS("g.mapsets", flags=c("l"))
  # list mapsets in current search path
  execGRASS("g.mapsets", flags=c("p"))
}
# if creating mapset for the first time:
if (watershed.isnew) {
  execGRASS("g.mapset", flags="c", parameters=list(mapset=watershed, location='vic_routing'))
  execGRASS("g.mapsets", parameters=list(mapset=watershed, operation='add'))
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

if (verbose){
  # make sure we have all the necessary layers
  execGRASS("g.list", flags="f", parameters=list(type='rast'))
  execGRASS("g.list", flags="f", parameters=list(type='vect'))
}

### Create Condidtioned DEM and Flow Accumulation ###

# Mask All Raster Operations To Watershed Region
  # unfortunately simply adding a mask sourced from a vector does not have any options on what
  # to do about partial cells on boundary: must convert boundary to lines, lines to raster, and
  # merge with mask from polygon to make sure boundaries are included
execGRASS("v.db.addcolumn",
          parameters=list(map="ws", columns="merge int"))
execGRASS("v.db.update",
          parameters=list(map="ws", column="merge", value="1"))
execGRASS("v.dissolve",
          flags=c('overwrite'),
          parameters=list(input="ws", output="wsdissolve", column="merge", layer='1'))
execGRASS("v.type",
          flags=c('overwrite'),
          parameters=list(input="wsdissolve", output="wsboundary", from_type="boundary", to_type="line"))
execGRASS("v.category",
          flags=c('overwrite'),
          parameters=list(input="wsboundary", output="wsboundarynamed", type="line", option="add", cat=as.integer(1)))
execGRASS("v.clean",
          flags=c('overwrite'),
          parameters=list(input="wsboundarynamed", output="wsboundaryline", type="line", tool="rmdac"))
execGRASS("v.to.rast",
          flags=c('overwrite'),
          parameters=list(input="wsboundaryline", output="wsboundaryraster", use='val', value=1))
execGRASS("v.to.rast",
          flags=c('overwrite'),
          parameters=list(input="wsdissolve", output="wsarearaster", use='val', value=1))
execGRASS("r.mapcalc",
          flags=c('overwrite'),
          parameters=list(expression="ws_mask='wsarearaster'||'wsboundaryraster'"))
execGRASS("r.mask", parameters=list(raster="ws_mask"))

# Condidtion DEM and Create Flow Accumulation
  # METHOD 1: create a filled dem, burn streams, pipe to r.terraflow (r.flow possible as well)
execGRASS("g.region",
          parameters=list(rast="dem-15"))
execGRASS("r.fill.dir",
          flags="overwrite",
          parameters=list(input='dem-15', output="dem-filled-15", outdir="dem-filled-dir-15"))
#execGRASS("r.carve", flags="n", parameters=list(rast="dem-filled-15", vect="stream", output="dem-carved-15")) #takes FOREVER!!!
execGRASS("r.fill.dir",
          flags="overwrite",
          parameters=list(input='dem-carved-15', output="dem-filled-carved-15", outdir="dem-filled-carved-dir-15"))
execGRASS("r.terraflow",
          flags="overwrite",
          parameters=list(elevation="dem-filled-carved-15", drainage='flow-dir-15', accumulation="flow-accumulation-tf-15"))

  # METHOD 2: using r.hydrodem with minimal corrections, pipe to r.watershed
execGRASS("g.region",
          parameters=list(rast="dem-15"))
execGRASS("r.hydrodem",
          parameters=list(input='dem-15', output="dem-hydrodem-15"))
execGRASS("r.watershed",
          flags=c("overwrite", "s", "b"),
          parameters=list(elevation="dem-hydrodem-15", accumulation="flow-accumulation-ws-15", drainage="flow-dir-ws-15"))
# r.watershed uses negative values for outflow values on perimeter, must correct
execGRASS("r.mapcalc", parameters=list(expression="'flow-accumulation-ws-15-abs'=abs('flow-accumulation-ws-15')"))

execGRASS("r.stats", flags=c('p'), parameters=list(input='flow-accumulation-ws-15-abs'))

# Export Condidtioned Dem For make_rout.sh
execGRASS("r.mask", flags=c("r")) #get rid of mask, it makes output funny...
execGRASS("r.out.arc", flags=c("overwrite"), parameters=list(input='flow-accumulation-ws-15-abs', output="flow-acc-15.asc"))
execGRASS("r.out.arc", flags=c("overwrite"), parameters=list(input='flow-dir-ws-15', output="flow-dir-15.asc"))

### From Flow Accumulation, invoke make_rout.sh to create 1/16th Flow Direction ###
A <- system2("./make_rout.sh")
if (A != 0) { stop("Routing script had errors") }

execGRASS("r.in.arc", flags=c("overwrite"), parameters=list(input='flow-dir-16th.asc', output='flow-dir-16th-vic'))


unlink_.gislock()
