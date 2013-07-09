#~ The flow direction file tells the routing model how all of the grid 
#~ cells are connected in the routing net. The format is an arc/info ascii 
#~ grid. It contains a 6-line header that tells the routing model the lower 
#~ left latitude and longitude, the number of rows and columns, and the 
#~ grid cell resolution.

library(spgrass6)
source('config.r')

tryCatch({
  ## Load in existing location
  loc <- initGRASS(gisBase=gisBase, gisDbase=gisDbase, location=location, mapset='PERMANENT', override=TRUE)

  if (verbose){
    ## list all available mapsets
    execGRASS("g.mapsets", flags=c("l"))
    ## list mapsets in current search path
    execGRASS("g.mapsets", flags=c("p"))
  }

  ## if creating mapset for the first time
  x <- execGRASS("g.mapset", flags="c", parameters=list(mapset=watershed, location=location))

  if (x != 0) {
    ## watershed was already created, just switch into it
    x <- execGRASS("g.mapset", parameters=list(mapset=watershed))
    if (x != 0) {
      print('Unable to create or switch into previously created mapset... something is up and needs to be looked into')
      print('Likely just need to remove the latent .gislock file in the gisDbase/location/watershed directory')
      stop('Mapset creation/switch error')
    }
  }

  if (verbose){
    ## list all available mapsets
    execGRASS("g.mapsets", flags=c("l"))
    ## list mapsets in current search path
    execGRASS("g.mapsets", flags=c("p"))
  }


  ## watershed creation successful, must do prepwork
  ## create watershed boundary based on subbasin selections
  ## d <- dirname(cwb)
  ## f <- sub("\\.[^.]*$", "", basename(cwb))
  query <- paste("WTRSHDGRPC IN ('", paste(subbasins, collapse="', '"), "')", sep='')
  print(query)
  ## x <- execGRASS("v.in.ogr", flags=c('o','overwrite'), parameters=list(dsn=d, layer=f, where=query, output="ws"))
  x <- execGRASS("v.extract", flags=c('d','overwrite'), parameters=list(input="cwb@PERMANENT", output="ws", where=query))
  if (x != 0) { stop('Unable to create watershed boundary from subbasin query')}

  x <- execGRASS("v.select", flags=c('overwrite'), parameters=list(ainput="hydat@PERMANENT", binput="ws", output="hydat_ws"))
  if (x != 0) { stop('Unable to select hydat points within watershed boundary')}
  
  
  if (verbose){
    ## make sure we have all the necessary layers
    execGRASS("g.list", flags="f", parameters=list(type='rast'))
    execGRASS("g.list", flags="f", parameters=list(type='vect'))
  }

  ## Mask All Raster Operations To Watershed Region
  ## unfortunately simply adding a mask sourced from a vector does not have any options on what
  ## to do about partial cells on boundary: must convert boundary to lines, lines to raster, and
  ## merge with mask from polygon to make sure boundaries are included.
  ## First remove all intermediate or output MASK layers
  execGRASS("g.remove", parameters=list(rast="wsboundaryraster,wsarearaster,ws_mask,MASK", vect="wsdissolve,wsboundary,wsboundarynamed,wsboundaryline"))
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
  
  ## Condidtion DEM and Create Flow Accumulation

  ## First must remove any previous layers that could exist if there was a previous run
  execGRASS("g.remove",
            parameters=list(rast="dem-filled-15,dem-filled-dir-15,dem-filled-carved-15,dem-filled-carved-dir-15,flow-dir-15,flow-accumulation-tf-15,dem-hydrodem-15,flow-accumulation-ws-15,flow-dir-ws-15,flow-accumulation-ws-15-abs"))

  execGRASS("g.region", parameters=list(rast="dem-15"))

  if (method == 1){
    ## METHOD 1: create a filled dem, burn streams, pipe to r.terraflow (r.flow possible as well)
    execGRASS("r.fill.dir",
              flags="overwrite",
              parameters=list(input='dem-15', output="dem-filled-15", outdir="dem-filled-dir-15"))
    ##execGRASS("r.carve", flags="n", parameters=list(rast="dem-filled-15", vect="stream", output="dem-carved-15")) #takes FOREVER!!!
    execGRASS("r.fill.dir",
              flags="overwrite",
              parameters=list(input='dem-filled-15', output="dem-filled-carved-15", outdir="dem-filled-carved-dir-15"))
    execGRASS("r.terraflow",
              flags="overwrite",
              parameters=list(elevation="dem-filled-carved-15", drainage='flow-dir-15', accumulation="flow-accumulation-tf-15"))
  }
  if (method == 2) {
    ## METHOD 2: using r.hydrodem with minimal corrections, pipe to r.watershed
    execGRASS("g.region",
              parameters=list(rast="dem-15"))
    execGRASS("r.hydrodem",
              flags=c("overwrite"),
              parameters=list(input='dem-15', output="dem-hydrodem-15"))
    execGRASS("r.watershed",
              flags=c("overwrite", "s", "b"),
              parameters=list(elevation="dem-hydrodem-15", accumulation="flow-accumulation-ws-15", drainage="flow-dir-ws-15"))
    ## r.watershed uses negative values for outflow values on perimeter, must correct
    execGRASS("r.mapcalc", parameters=list(expression="'flow-accumulation-ws-15-abs'=abs('flow-accumulation-ws-15')"))

    execGRASS("r.stats", flags=c('p'), parameters=list(input='flow-accumulation-ws-15-abs'))
  }

  if (verbose) {
    execGRASS("g.region", flags=c('p'))
  }
  ## Export Condidtioned Dem For make_rout.sh
  code.dir <- getwd()
  setwd(tempfiles)
  execGRASS("r.mask", flags=c("r")) #get rid of mask, it makes output funny...
  execGRASS("r.out.arc", flags=c("overwrite"), parameters=list(input='flow-accumulation-ws-15-abs', output="flow-acc-15.asc"))
  execGRASS("r.out.arc", flags=c("overwrite"), parameters=list(input='flow-dir-ws-15', output="flow-dir-15.asc"))

  ## From Flow Accumulation, invoke make_rout.sh to create 1/16th Flow Direction ###
  print("Next command to run")
  print(paste(file.path(code.dir, "make_rout.sh"),
              file.path(tempfiles, 'flow-acc-15.asc'),
              file.path(tempfiles, 'flow-dir-16th.asc'),
                     sep=' '))
}, error = function(e) {
  e
}, finally = {
  print("unlinking gislock")
  unlink_.gislock()
})
