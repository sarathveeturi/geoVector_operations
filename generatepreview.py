import urllib
from io import BytesIO

# import pngcanvas
import requests
import shapefile
from PIL import Image, ImageDraw


def generatepreview(shapefile_name):
    r = shapefile.Reader(shapefile_name)

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
    wmsbounds = f"{str(bounds[1])},{str(bounds[0])},{str(bounds[3])},{str(bounds[2])}"

    # Iterate through all the shapes within the shapefile and draw them onto the PNGCanvas before saving the canvas as a PNG file
    xratio = iwidth / xdist
    yratio = iheight / ydist
    pixels = []

    size = iwidth, iheight

    url = "https://ows.terrestris.de/osm/service"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "LAYERS": "TOPO-OSM-WMS",
        "TILED": "false",
        "WIDTH": str(iwidth),
        "HEIGHT": str(iheight),
        "CRS": "EPSG:4326",  # will break near n/s poles, but required by service
        "STYLES": "",
        "BBOX": wmsbounds,
    }
    payload_str = urllib.parse.urlencode(params, safe=":+-/.,")
    try:
        response = requests.get(url, params=payload_str)
        background = response.content
    except Exception as e:
        print(
            "Failed to fetch background from OSM, the generated preview will only contain shapefile features."
        )
        print(e)

    with Image.open(BytesIO(background)) as im:
        draw = ImageDraw.Draw(im)
        im.thumbnail(size)
        for shape in r.shapes():
            for x, y in shape.points:
                px = int(iwidth - ((r.bbox[2] - x) * xratio))
                py = int((r.bbox[3] - y) * yratio)
                pixels.append((px, py))
            draw.line(pixels, fill="red")
            pixels = []
        im.save("%s.png" % shapefile_name, "PNG")
        print("Preview saved to: (%s.png" % shapefile_name)

    # Create a world file
    wld = open("%s.pgw" % shapefile_name, "w")
    wld.write("%s\n" % (xdist / iwidth))
    wld.write("0.0\n")
    wld.write("0.0\n")
    wld.write("-%s\n" % (ydist / iheight))
    wld.write("%s\n" % r.bbox[0])
    wld.write("%s\n" % r.bbox[3])
    wld.close
