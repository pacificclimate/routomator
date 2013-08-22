library(rgdal)
source('config.r')

get.watershed.boundary <- function(watershed) {
	switch(watershed,
		columbia={
			fp <- '/home/data/projects/hydrology/vic/data/routomator/watersheds/columbia_reduced.shp'
			d <- dirname(fp)
			f <- sub("\\.[^.]*$", "", basename(fp))
			ws.ogr <- readOGR(d, f, stringsAsFactors = FALSE)
			return(ws.ogr)
		},
		peace={
			fp <- '/home/data/gis/vic_final_peace/cwb_peace_merged.shp'
			d <- dirname(fp)
			f <- sub("\\.[^.]*$", "", basename(fp))
			ws.ogr <- readOGR(d, f, stringsAsFactors = FALSE)
			return(ws.ogr)
		},
		{
			error('Unknown watershed')
		}
	)
}
