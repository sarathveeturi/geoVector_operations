import glob
import os
import urllib
from io import BytesIO

import fiona
import geopandas as gpd
import requests
import shapefile
from PIL import Image, ImageDraw

#shp_file = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/shapefiles/fredericton_roads.shp'
#shp_file = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/shapefiles/Drillholes_Dataset/Drillholes_Dataset.shp'
#shp_file = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/shapefiles/geonb_pan_ncb_shp/geonb_pan_ncb.shp'
#Op = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/shapefiles/Drillholes_Dataset/'
#Op = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/shapefiles/'
#Op = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/shapefiles/geonb_pan_ncb_shp/'

kml_file = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/KMZ/doc.kml'
kml_Op = 'C:/Users/ssara/Documents/my_drive/vector_processing_builds/thematic_layers/KMz/'



def shapefile_preview(shapefile_name, override_output=None):
    r = shapefile.Reader(shapefile_name)
    file = fiona.open(shapefile_name)
    geom_type = file.meta['schema']['geometry']
    print(geom_type)

    # Determine bounding box x and y distances and then calculate an xyratio
    # that can be used to determine the size of the generated PNG file. A xyratio
    # of greater than one means that PNG is to be a landscape type image whereas
    # an xyratio of less than one means the PNG is to be a portrait type image.
    xdist = r.bbox[2] - r.bbox[0]
    ydist = r.bbox[3] - r.bbox[1]
    xyratio = xdist / ydist
    image_max_dimension = 600  # Change this to desired max dimension of generated PNG
    if xyratio >= 1:
        iwidth = image_max_dimension
        iheight = int(image_max_dimension / xyratio)
    else:
        iwidth = int(image_max_dimension / xyratio)
        iheight = image_max_dimension

    bounds = r.bbox

    # Iterate through all the shapes within the shapefile and draw them onto the PNGCanvas before saving the canvas as a PNG file
    xratio = iwidth / xdist
    yratio = iheight / ydist
    pixels = []

    size = iwidth, iheight
    background = get_background_image(bounds, size)
    with Image.open(BytesIO(background)) as im:
        draw = ImageDraw.Draw(im)
        im.thumbnail(size)
        for shape in r.shapes():
            for x, y in shape.points:
                px = int(iwidth - ((r.bbox[2] - x) * xratio))
                py = int((r.bbox[3] - y) * yratio)
                pixels.append((px, py))
            if geom_type == "MultiPoint" or geom_type =="Point":
                #print("drawing the points......................")
                draw.ellipse((px, py,px+10,py+10),fill="red")
            elif geom_type =="3D Polygon":
                #print(pixels[0], pixels[1], pixels[2], pixels[3])
                draw.polygon((pixels[0], pixels[1], pixels[2], pixels[3]), fill="red")
            else:
                draw.line(pixels, fill="red")
            pixels = []  
        if override_output is not None:
            im.save("%s.png" % override_output, "PNG")
            print("Preview saved to: %s.png" % override_output)
        else:
            im.save("%s.png" % shapefile_name, "PNG")
            print("Preview saved to: %s.png" % shapefile_name)

    # Create a world file (optional but potentially useful)
    wld = open("%s.pgw" % shapefile_name, "w")
    wld.write("%s/n" % (xdist / iwidth))
    wld.write("0.0/n")
    wld.write("0.0/n")
    wld.write("-%s/n" % (ydist / iheight))
    wld.write("%s/n" % r.bbox[0])
    wld.write("%s/n" % r.bbox[3])
    wld.close


def kml_preview(kml_name):
    print("kml preview:", kml_name)
    fiona.drvsupport.supported_drivers["kml"] = "rw"
    fiona.drvsupport.supported_drivers[
        "KML"
    ] = "rw"  # enable KML support which is disabled by default
    tempfile = "tmp.shp"
    gdf = gpd.read_file(kml_name, driver='KML')
    gdf.to_file(tempfile)
    shapefile_preview(
        tempfile, override_output=kml_name
    )  # this is cheating but takes minimal time and saves us from needing to support the very wide range of kml features
    for f in glob.glob("tmp.*"):
        os.remove(f)


def geojson_preview(geojson_name):
    tempfile = "tmp.shp"
    gdf = gpd.read_file(geojson_name)
    gdf.to_file(tempfile)
    shapefile_preview(tempfile, override_output=geojson_name)
    for f in glob.glob("tmp.*"):
        os.remove(f)


def get_background_image(bounds, size):
    print(bounds, size)
    wmsbounds = f"{str(bounds[1])},{str(bounds[0])},{str(bounds[3])},{str(bounds[2])}"

    url = "https://ows.terrestris.de/osm/service"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "LAYERS": "TOPO-OSM-WMS",
        "TILED": "false",
        "WIDTH": str(size[0]),
        "HEIGHT": str(size[1]),
        "CRS": "EPSG:4326",  # will break near n/s poles, but required by service
        "STYLES": "",
        "BBOX": wmsbounds,
    }
    payload_str = urllib.parse.urlencode(params, safe=":+-/.,")
    try:
        response = requests.get(url, params=payload_str)
        background = response.content
        return background

    except:  # noqa: E722 (No need to list connection and timeout errors)
        print(
            "Failed to fetch background from OSM, the generated preview will only contain shapefile features."
        )

kml_preview(kml_file)