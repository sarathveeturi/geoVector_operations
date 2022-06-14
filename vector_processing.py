import os
import glob
import fiona
import shapefile
from osgeo import gdal
import geopandas as gpd
from fastkml import kml
import kml2geojson.main as kml2gMain

# path to the directory containing thematic files. Every shapefile must have it's associated .cpg, .dbf, .prj, .shp, .shx files. '.dbf' and '.shx' and '.shp' are mandatory.
thematicFile_path = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/KML/'

#if an individual file needs to be passed instead of a folder, the script uses 'individual_thematicFile_path' and proceeds forward
individual_thematicFile_path = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/KML/Crown_Lands.kml'
#kmlFile_directory = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematicFile/KML/CrownLands.kml'

#path or location where the geoJSON files have to be stored.
output_path = "C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/geojson_files/"

# following method reprojects thematic files into WGS84 and saves it to a geoJSON file which can be pulled into the Leaflet code
def process_thematic_layer():
	if os.path.exists(thematicFile_path):
		for thematicFile in os.listdir(thematicFile_path):
			filepath = os.path.join(thematicFile_path, thematicFile)
			filename = os.path.split(filepath)
			
			if filename[1].endswith('.shp'):
				print("Converting Shapefile into geojson.........................")
				thematicFile = gpd.read_file(thematicFile_path)
				#with gpd.read_file(filename[1]) as thematicFile:
				them_lyr_projection = thematicFile.crs
				# check the CRS of the thematic layer and depending upon the CRS, either SET or TRANSFORM or directly convert the thematic layer into corresponding geoJSON file
				# Sets the shapefile's CRS into WGS84
				if them_lyr_projection == None:
					thematic_file_wgs84 = thematicFile.set_crs("EPSG:4326")
					# saving the geoJSON to the output path
					thematic_file_wgs84.to_file(output_path + filename[1] + '.geojson', driver='GeoJSON')
				elif them_lyr_projection !='epsg: 4326':
					#print("inside elif!!!!!!!!!!!!!!!!!!")
					# converts the shapefile's CRS into WGS84
					thematic_file_wgs84 = thematicFile.to_crs("EPSG:4326")
					# saving the geoJSON to the output path
					thematic_file_wgs84.to_file(output_path + filename[1] + '.geojson', driver='GeoJSON')
				else:
					# print("inside else!!!!!!!!!!!!!!!")
					# saving the geoJSON to the output path
					thematic_file_wgs84.to_file(output_path + filename[1] + '.geojson', driver='GeoJSON')
			elif filename[1].endswith('.kml'):
				print("Converting the KML file to geojson..............")
				print(filepath)
				kml2gMain.convert(filepath, output_path)
				
			elif filename[1].endswith('csv'):
				print("Converting the CSV file to geojson.............")

			else:
				print(filepath)
				print("Unsupported files have been uploaded!!!!!!!!!!!!!!!!!!!!")
	else:
		break

	if os.path.exists(individual_thematicFile_path):
		if os.path.split(individual_thematicFile_path)[1].endswith('.kml'):
			kml2gMain.convert(individual_thematicFile_path, output_path)
		elif os.path.split(individual_thematicFile_path)[1].endswith('.shp'):
			thematicFile = gpd.read_file(thematicFile_path)
				#with gpd.read_file(filename[1]) as thematicFile:
				them_lyr_projection = thematicFile.crs
				# check the CRS of the thematic layer and depending upon the CRS, either SET or TRANSFORM or directly convert the thematic layer into corresponding geoJSON file
				# Sets the shapefile's CRS into WGS84
				if them_lyr_projection == None:
					thematic_file_wgs84 = thematicFile.set_crs("EPSG:4326")
					# saving the geoJSON to the output path
					thematic_file_wgs84.to_file(output_path + os.path.split(individual_thematicFile_path)[1] + '.geojson', driver='GeoJSON')
				elif them_lyr_projection !='epsg: 4326':
					#print("inside elif!!!!!!!!!!!!!!!!!!")
					# converts the shapefile's CRS into WGS84
					thematic_file_wgs84 = thematicFile.to_crs("EPSG:4326")
					# saving the geoJSON to the output path
					thematic_file_wgs84.to_file(output_path + os.path.split(individual_thematicFile_path)[1] + '.geojson', driver='GeoJSON')
				else:
					# print("inside else!!!!!!!!!!!!!!!")
					# saving the geoJSON to the output path
					thematic_file_wgs84.to_file(output_path + os.path.split(individual_thematicFile_path)[1] + '.geojson', driver='GeoJSON')
		else:
			Print("Searching for a shapefile/KML file")

process_thematic_layer()

			
			

			

		

	
