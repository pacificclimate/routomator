#~ The flow direction file tells the routing model how all of the grid 
#~ cells are connected in the routing net. The format is an arc/info ascii 
#~ grid. It contains a 6-line header that tells the routing model the lower 
#~ left latitude and longitude, the number of rows and columns, and the 
#~ grid cell resolution.

library(spgrass6)
source('config.r')
source('watershed.r')

code.dir <- getwd()

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
  x <- execGRASS("g.mapset", flags=c("c", "quiet"), parameters=list(mapset=watershed, location=location))

  if (x != 0) {
    ## watershed was already created, just switch into it
    x <- execGRASS("g.mapset", parameters=list(mapset=watershed))
    if (x != 0) {
      print('Unable to create or switch into previously created mapset... something is up and needs to be looked into')
      print('Likely just need to remove the latent .gislock file in the gisDbase/location/watershed directory')
      stop('Mapset creation/switch error')
    }
  }

  ## watershed creation successful, must do prepwork
  ## create watershed boundary based on subbasin selections

  execGRASS("g.remove", flags=c("quiet"), parameters=list(vect="ws"))
  ws = get.watershed.boundary(watershed)
  x <- writeVECT6(ws, 'ws', v.in.ogr_flags=c('o'))
  if (x != 0) { stop('Unable to create watershed boundary from subbasin query')}

  x <- execGRASS("v.select", flags=c('overwrite', 'quiet'), parameters=list(ainput="hydat@PERMANENT", binput="ws", output="hydat_ws"))
  if (x != 0) { stop('Unable to select hydat points within watershed boundary')}
  
  # Export hydat as csv to tempdir
  file.remove(file.path(tempfiles, 'hydat_ws.csv'))
  execGRASS("v.out.ogr", flags=c('overwrite', 'quiet'), parameters=list(format="CSV", input="hydat_ws", dsn=file.path(tempfiles, 'hydat_ws.csv')))
  execGRASS("v.out.ogr", flags=c('overwrite', 'quiet'), parameters=list(format="ESRI_Shapefile", input="hydat_ws", dsn=file.path(outdir, 'hydat_ws.shp')))
  
  ## Mask All Raster Operations To Watershed Region

  execGRASS("g.remove", flags=c("quiet"), parameters=list(rast="MASK,ws_mask"))
  execGRASS("r.in.arc", flags=c('overwrite', 'quiet'), parameters=list(input=file.path(outdir, 'mask.asc'), output='ws_mask'))
  execGRASS("r.mask", parameters=list(raster="ws_mask"))
  
  ## Condidtion DEM and Create Flow Accumulation

  ## First must remove any previous layers that could exist if there was a previous run
  execGRASS("g.remove",
            parameters=list(rast="dem-hydrodem,flow-acc-15,flow-dir-15,flow-acc-15-abs"))

  execGRASS("g.region", parameters=list(rast="dem"))

  # This next part often fails with the hydrodem module being accessed through R.
  # If it fails, you must manually start a grass session in the location/watershed directory
  # (cd to GISBASE/location/watershed, then start grass70), then add the PERMANENT mapset:
  # g.mapsets addmapset=PERMANENT, then switch back to the watershed mapset
  # g.mapset mapset=YOURWATERSHED, then you should be able to run the command
  # r.hydrodem --overwrite input=dem output=dem-hydrodem-15
  # Then re-run this script, commenting ou the next line.
  execGRASS("r.hydrodem", flags=c("overwrite"), parameters=list(input='dem', output="dem-hydrodem"))

  execGRASS("r.watershed",
            flags=c("overwrite", "s", "b"),
            parameters=list(elevation="dem-hydrodem", accumulation="flow-acc-15", drainage="flow-dir-15"))
  ## r.watershed uses negative values for outflow values on perimeter, must correct
  execGRASS("r.mapcalc", flags=c("overwrite"), parameters=list(expression="'flow-acc-15-abs'=abs('flow-acc-15')"))

  ## Export Condidtioned Dem For make_rout.sh
  code.dir <- getwd()
  setwd(tempfiles)
  execGRASS("r.mask", flags=c("r")) #get rid of mask, it makes output funny...
  execGRASS("r.out.arc", flags=c("overwrite"), parameters=list(input='flow-acc-15-abs', output="flow-acc-15.asc"))
  execGRASS("r.out.arc", flags=c("overwrite"), parameters=list(input='flow-dir-15', output="flow-dir-15.asc"))

  ## From Flow Accumulation, invoke make_rout.sh to create 1/16th Flow Direction ###
  print("Next command to run")
  print(paste(file.path("flowgen", "make_rout.sh"),
              file.path(tempfiles, 'flow-acc-15.asc'),
              file.path(tempfiles, 'flow-dir-16th.asc'),
                     sep=' '))
}, error = function(e) {
  e
}, finally = {
  print("unlinking gislock")
  unlink_.gislock()
})
