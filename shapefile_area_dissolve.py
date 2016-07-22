# coding=latin-1
# to clear command prompt: cls <return>

import os
import arcpy
import glob

##Notice there is no storage in this path
indir = 'H:/home/wernera/tmp/routomator/'

arcpy.env.workspace = indir
arcpy.env.overwriteOutput = True

shps = glob.glob(indir + "catchment*.shp")
shps = [x for x in shps if 'albers' not in x]
shps = [x for x in shps if 'dissolve' not in x]
install_dir = arcpy.GetInstallInfo()['InstallDir']
bc_albers = os.path.join(install_dir, r"Coordinate Systems/Projected Coordinate Systems/National Grids/Canada/NAD 1983 CSRS BC Environment Albers.prj")
outCS = arcpy.SpatialReference(bc_albers)

projected_shapes = []

total = len(shps)
i = 0
for shp in shps:
    name = os.path.splitext(os.path.basename(shp))[0].split('_')[1]
    print '[{0}/{1}]: {2}'.format(i, total, name)
    i += 1
    
    # Dissolve and Project to Albers
    dissolveFields = ["DN"]
    shpdissolve = os.path.splitext(os.path.basename(shp))[0] + "_dissolve.shp"
    arcpy.Dissolve_management(shp, shpdissolve, dissolveFields, "", "MULTI_PART", "DISSOLVE_LINES")
    projected_shape = os.path.splitext(os.path.basename(shp))[0] + "_albers.shp"
    projected_shapes.append(projected_shape)
    if os.path.exists(os.path.join(indir, projected_shape)):
        # print os.path.splitext(projected_shape)[0]
        # print os.path.join(indir, os.path.splitext(projected_shape)[0])
        files = glob.glob(os.path.join(indir, os.path.splitext(projected_shape)[0]) + '*')
        # print files
        for f in files:
            os.remove(f)
    arcpy.Project_management(shpdissolve, projected_shape, "PROJCS['NAD_1983_BC_Environment_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',1000000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-126.0],PARAMETER['Standard_Parallel_1',50.0],PARAMETER['Standard_Parallel_2',58.5],PARAMETER['Latitude_Of_Origin',45.0],UNIT['Meter',1.0]]", "NAD_1983_To_WGS_1984_1", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")

    # Add name field
    arcpy.management.AddField(projected_shape, 'ID', 'TEXT')
    arcpy.CalculateField_management(projected_shape, 'ID', repr(name), "PYTHON_9.3")

    # Calculate Area
    arcpy.management.AddField(projected_shape, 'AREA', 'FLOAT')
    arcpy.CalculateField_management(projected_shape, 'AREA', 'float(!SHAPE.area!)/1000000', "PYTHON")
    
arcpy.management.Merge(projected_shapes, "merged.shp")
