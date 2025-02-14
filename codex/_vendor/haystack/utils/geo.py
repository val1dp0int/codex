from codex._vendor.haystack.constants import WGS_84_SRID
from codex._vendor.haystack.exceptions import SpatialError


def ensure_geometry(geom):
    """
    Makes sure the parameter passed in looks like a GEOS ``GEOSGeometry``.
    """
    if not hasattr(geom, "geom_type"):
        raise SpatialError("Point '%s' doesn't appear to be a GEOS geometry." % geom)

    return geom


def ensure_point(geom):
    """
    Makes sure the parameter passed in looks like a GEOS ``Point``.
    """
    ensure_geometry(geom)

    if geom.geom_type != "Point":
        raise SpatialError("Provided geometry '%s' is not a 'Point'." % geom)

    return geom


def ensure_wgs84(point):
    """
    Ensures the point passed in is a GEOS ``Point`` & returns that point's
    data is in the WGS-84 spatial reference.
    """
    ensure_point(point)
    # Clone it so we don't alter the original, in case they're using it for
    # something else.
    new_point = point.clone()

    if not new_point.srid:
        # It has no spatial reference id. Assume WGS-84.
        new_point.srid = WGS_84_SRID
    elif new_point.srid != WGS_84_SRID:
        # Transform it to get to the right system.
        new_point.transform(WGS_84_SRID)

    return new_point


def ensure_distance(dist):
    """
    Makes sure the parameter passed in is a 'Distance' object.
    """
    try:
        # Since we mostly only care about the ``.km`` attribute, make sure
        # it's there.
        dist.km
    except AttributeError:
        raise SpatialError("'%s' does not appear to be a 'Distance' object." % dist)

    return dist


def generate_bounding_box(bottom_left, top_right):
    """
    Takes two opposite corners of a bounding box (order matters!) & generates
    a two-tuple of the correct coordinates for the bounding box.

    The two-tuple is in the form ``((min_lat, min_lng), (max_lat, max_lng))``.
    """
    west, lat_1 = bottom_left.coords
    east, lat_2 = top_right.coords
    min_lat, max_lat = min(lat_1, lat_2), max(lat_1, lat_2)
    return ((min_lat, west), (max_lat, east))
