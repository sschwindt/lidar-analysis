import geo_utils
from LasPoint import *
import webbrowser


def lookup_epsg(file_name):
    """
    Start a google search to retrieve information from a file name (or other ``str``) with information such as *UTM32*.
    Args:
        file_name (str): file name  or other string with words separated by "-" or "_"

    Note:
        Opens a google search in the default web browser.
    """
    search_string = file_name.replace("_", "+").replace(".", "+").replace("-", "+")
    google_qry = "https://www.google.com/?#q=projection+crs+epsg+"
    webbrowser.open(google_qry + search_string)


@log_actions
@cache
def process_file(source_file_name, epsg, **opts):
    """Load a las-file and convert it to another geospatial file format (**opts)

    Args:
        source_file_name (`str`): Full directory of the source file to use with methods
                             * if method="las2*" > provide a las-file name
                             * if method="shp2*" > provide a shapefile name
        epsg (int): Authority code to use (try lashy.lookup_epsg(las_file_name) to look up the epsg online).
        **opts: optional keyword arguments

    Keyword Args:
        create_dem (bool): Default=False - set to True for creating a digital elevation model (DEM)
        extract_attributes (str): Attributes to extract from the las-file available in pattr (config.py)
        methods(`list` [`str`]): Enabled list strings are las2shp, las2tif, shp2tif
        overwrite (bool): Overwrite existing shapefiles and/or GeoTIFFs (default=``True``).
        pixel_size (float): Use with *2tif  to set the size of pixels relative to base units (pixel_size=5 > 5-m pixels)
        shapefile_name (str): Name of the point shapefile to produce with las2*
        tif_prefix (str): Prefix include folder path to use for GeoTiFFs (defined extract_attributes are appended to file name)

    Returns:
        bool: True if successful, False otherwise
    """

    default_keys = {"extract_attributes": "aci",
                    "methods": ["las2shp"],
                    "shapefile_name": os.path.abspath("") + "/{0}.shp".format(source_file_name.split(".")[0]),
                    "tif_prefix": os.path.abspath("") + "/{0}_".format(source_file_name.split(".")[0]),
                    "overwrite": True,
                    "create_dem": False,
                    "pixel_size": 1.0,
                    }

    for k in default_keys.keys():
        if opts.get(k):
            default_keys[k] = opts.get(k)

    las_object = LasPoint(las_file_name=source_file_name,
                          epsg=epsg,
                          use_attributes=default_keys["extract_attributes"],
                          overwrite=default_keys["overwrite"])

    if "las2shp" in default_keys["methods"] or not os.path.isfile(default_keys["shapefile_name"]):
        las_object.export2shp(shapefile_name=default_keys["shapefile_name"])

    if not os.path.isfile(default_keys["shapefile_name"]):
        logging.warning("Shapefile %s not found. Cannot continue." % default_keys["shapefile_name"])
        return False
    else:
        logging.info(" * Using %s to create GeoTIFF(s)." % default_keys["shapefile_name"])

    if "2tif" in "".join(default_keys["methods"]):
        for attr in default_keys["extract_attributes"]:
            tif_name = "{0}{1}.tif".format(default_keys["shapefile_name"], wattr[attr])
            geo_utils.rasterize(in_shp_file_name=default_keys["shapefile_name"],
                                out_raster_file_name=tif_name,
                                pixel_size=default_keys["pixel_size"],
                                field_name=wattr[attr],
                                overwrite=default_keys["overwrite"])
    return True
