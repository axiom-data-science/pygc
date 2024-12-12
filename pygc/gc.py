from pyproj import Geod
import numpy as np


def great_circle(**kwargs):
    """
        Named arguments:
        distance  = distance to travel, or numpy array of distances
        azimuth   = angle, in DEGREES of HEADING from NORTH, or numpy array of azimuths
        latitude  = latitude, in DECIMAL DEGREES, or numpy array of latitudes
        longitude = longitude, in DECIMAL DEGREES, or numpy array of longitudes
        rmajor    = radius of earth's major axis. default=6378137.0 (WGS84)
        rminor    = radius of earth's minor axis. default=6356752.3142 (WGS84)

        Returns a dictionary with:
        'latitude' in decimal degrees
        'longitude' in decimal degrees
        'reverse_azimuth' in decimal degrees

    """
    distance = kwargs.get('distance')
    azimuth = kwargs.get('azimuth')
    latitude = kwargs.get('latitude')
    longitude = kwargs.get('longitude')
    rmajor = kwargs.get('rmajor', 6378137.0)
    rminor = kwargs.get('rminor', 6356752.3142)

    # Convert inputs to numpy arrays if they are not already
    distance = np.atleast_1d(distance)
    azimuth = np.atleast_1d(azimuth)
    latitude = np.atleast_1d(latitude)
    longitude = np.atleast_1d(longitude)

    # Ensure all arrays have the same length
    max_length = max(len(distance), len(azimuth), len(latitude), len(longitude))
    if len(distance) != max_length:
        distance = np.full(max_length, distance[0])
    if len(azimuth) != max_length:
        azimuth = np.full(max_length, azimuth[0])
    if len(latitude) != max_length:
        latitude = np.full(max_length, latitude[0])
    if len(longitude) != max_length:
        longitude = np.full(max_length, longitude[0])

    geod = Geod(a=rmajor, b=rminor)
    lon, lat, back_azimuth = geod.fwd(longitude, latitude, azimuth, distance)

    if isinstance(back_azimuth, (list, np.ndarray)):
        back_azimuth = np.array([i % 360 for i in back_azimuth])
    else:
        back_azimuth = back_azimuth % 360

    return {
        'latitude': np.array(lat) if isinstance(lat, (list, np.ndarray)) else lat,
        'longitude': np.array(lon) if isinstance(lon, (list, np.ndarray)) else lon,
        'reverse_azimuth': back_azimuth if isinstance(back_azimuth, (list, np.ndarray)) else back_azimuth
    }


def great_distance(**kwargs):
    """
        Named arguments:
        start_latitude  = starting latitude, in DECIMAL DEGREES
        start_longitude = starting longitude, in DECIMAL DEGREES
        end_latitude    = ending latitude, in DECIMAL DEGREES
        end_longitude   = ending longitude, in DECIMAL DEGREES
        rmajor          = radius of earth's major axis. default=6378137.0 (WGS84)
        rminor          = radius of earth's minor axis. default=6356752.3142 (WGS84)

        Returns a dictionary with:
        'distance' in meters
        'azimuth' in decimal degrees
        'reverse_azimuth' in decimal degrees

    """
    final_mask = None
    start_latitude = kwargs.get('start_latitude')
    start_longitude = kwargs.get('start_longitude')
    end_latitude = kwargs.get('end_latitude')
    end_longitude = kwargs.get('end_longitude')
    rmajor = kwargs.get('rmajor', 6378137.0)
    rminor = kwargs.get('rminor', 6356752.3142)

    # Handle cases where inputs are mask arrays
    if (np.ma.isMaskedArray(start_latitude) or
        np.ma.isMaskedArray(start_longitude) or
        np.ma.isMaskedArray(end_latitude) or
        np.ma.isMaskedArray(end_longitude)
       ):

        try:
            assert start_latitude.size == start_longitude.size == end_latitude.size == end_longitude.size
        except AttributeError:
            raise ValueError("All or none of the inputs should be masked")
        except AssertionError:
            raise ValueError("When using masked arrays all must be of equal size")

        final_mask = np.logical_not((start_latitude.mask | start_longitude.mask | end_latitude.mask | end_longitude.mask))
        if np.isscalar(final_mask):
            final_mask = np.full(start_latitude.size, final_mask, dtype=bool)
        start_latitude = start_latitude[final_mask].data
        start_longitude = start_longitude[final_mask].data
        end_latitude = end_latitude[final_mask].data
        end_longitude = end_longitude[final_mask].data

    # Handle cases where either start or end are multiple points
    else:
        start_latitude = np.atleast_1d(start_latitude)
        start_longitude = np.atleast_1d(start_longitude)
        end_latitude = np.atleast_1d(end_latitude)
        end_longitude = np.atleast_1d(end_longitude)
        varlist = [start_latitude, start_longitude, end_latitude, end_longitude]

        max_length = max([len(i) for i in varlist])
        if max_length > 1:
            for i in range(len(varlist)):
                if len(varlist[i]) == 1:
                    varlist[i] = np.full(max_length, varlist[i][0])
                else:
                    varlist[i] = np.array(varlist[i])

            start_latitude, start_longitude, end_latitude, end_longitude = varlist

    geod = Geod(a=rmajor, b=rminor)
    azimuth, back_azimuth, distance = geod.inv(start_longitude, start_latitude, end_longitude, end_latitude)

    if isinstance(back_azimuth, (list, np.ndarray)):
        back_azimuth = np.array([i % 360 for i in back_azimuth])
    else:
        back_azimuth = back_azimuth % 360

    if final_mask is not None:
        distance_d = np.ma.masked_all(final_mask.size, dtype=np.float64)
        azimuth_d = np.ma.masked_all(final_mask.size, dtype=np.float64)
        back_azimuth_d = np.ma.masked_all(final_mask.size, dtype=np.float64)

        distance_d[final_mask] = distance
        azimuth_d[final_mask] = azimuth
        back_azimuth_d[final_mask] = back_azimuth
        
        return {
            'distance': distance_d,
            'azimuth': azimuth_d,
            'reverse_azimuth': back_azimuth_d
        }
    
    else:
        return {
            'distance': np.array(distance) if isinstance(distance, (list, np.ndarray)) else distance,
            'azimuth': np.array(azimuth) if isinstance(azimuth, (list, np.ndarray)) else azimuth,
            'reverse_azimuth': back_azimuth if isinstance(back_azimuth, (list, np.ndarray)) else back_azimuth
        }
