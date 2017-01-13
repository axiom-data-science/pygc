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

    distance  = kwargs.pop('distance')
    azimuth   = np.radians(kwargs.pop('azimuth'))
    latitude  = np.radians(kwargs.pop('latitude'))
    longitude = np.radians(kwargs.pop('longitude'))
    rmajor    = kwargs.pop('rmajor', 6378137.0)
    rminor    = kwargs.pop('rminor', 6356752.3142)
    f         = (rmajor - rminor) / rmajor

    vector_pt = np.vectorize(vinc_pt)
    lat_result, lon_result, angle_result = vector_pt(f, rmajor,
                                                     latitude,
                                                     longitude,
                                                     azimuth,
                                                     distance)
    return {'latitude': np.degrees(lat_result),
            'longitude': np.degrees(lon_result),
            'reverse_azimuth': np.degrees(angle_result)}


def great_distance(**kwargs):
    """
        Named arguments:
        start_latitude  = starting latitude, in DECIMAL DEGREES
        start_longitude = starting longitude, in DECIMAL DEGREES
        end_latitude    = ending latitude, in DECIMAL DEGREES
        end_longitude   = ending longitude, in DECIMAL DEGREES
        rmajor          = radius of earth's major axis. default=6378137.0 (WGS84)
        rminor          = radius of earth's minor axis. default=6356752.3142 (WGS84)

        Returns a dictionaty with:
        'distance' in meters
        'azimuth' in decimal degrees
        'reverse_azimuth' in decimal degrees

    """

    sy     = kwargs.pop('start_latitude')
    sx     = kwargs.pop('start_longitude')
    ey     = kwargs.pop('end_latitude')
    ex     = kwargs.pop('end_longitude')
    rmajor = kwargs.pop('rmajor', 6378137.0)
    rminor = kwargs.pop('rminor', 6356752.3142)
    f      = (rmajor - rminor) / rmajor

    vector_dist = np.vectorize(vinc_dist)

    if (np.ma.isMaskedArray(sy) or
        np.ma.isMaskedArray(sx) or
        np.ma.isMaskedArray(ey) or
        np.ma.isMaskedArray(ex)
       ):
        try:
            assert sy.size == sx.size == ey.size == ex.size
        except AttributeError:
            raise ValueError("All or none of the inputs should be masked")
        except AssertionError:
            raise ValueError("When using masked arrays all must be of equal size")

        final_mask = np.logical_not((sy.mask | sx.mask | ey.mask | ex.mask))
        if np.isscalar(final_mask):
            final_mask = np.full(sy.size, final_mask, dtype=bool)
        sy = sy[final_mask]
        sx = sx[final_mask]
        ey = ey[final_mask]
        ex = ex[final_mask]

        tmpd, tmpa, tmpra = vector_dist(f, rmajor,
                                        np.radians(sy),
                                        np.radians(sx),
                                        np.radians(ey),
                                        np.radians(ex))
        d = np.ma.masked_all(final_mask.size, dtype=np.float64)
        d[final_mask] = tmpd

        a = np.ma.masked_all(final_mask.size, dtype=np.float64)
        a[final_mask] = tmpa

        ra = np.ma.masked_all(final_mask.size, dtype=np.float64)
        ra[final_mask] = tmpra

    else:
        d, a, ra = vector_dist(f, rmajor,
                               np.radians(sy),
                               np.radians(sx),
                               np.radians(ey),
                               np.radians(ex))

    return {'distance': d,
            'azimuth': np.degrees(a),
            'reverse_azimuth': np.degrees(ra)}


# -----------------------------------------------------------------------
# | Algrothims from Geocentric Datum of Australia Technical Manual      |
# |                                                                     |
# | http://www.anzlic.org.au/icsm/gdatum/chapter4.html                  |
# |                                                                     |
# | This page last updated 11 May 1999                                  |
# |                                                                     |
# | Computations on the Ellipsoid                                       |
# |                                                                     |
# | There are a number of formulae that are available                   |
# | to calculate accurate geodetic positions,                           |
# | azimuths and distances on the ellipsoid.                            |
# |                                                                     |
# | Vincenty's formulae (Vincenty, 1975) may be used                    |
# | for lines ranging from a few cm to nearly 20,000 km,                |
# | with millimetre accuracy.                                           |
# | The formulae have been extensively tested                           |
# | for the Australian region, by comparison with results               |
# | from other formulae (Rainsford, 1955 & Sodano, 1965).               |
# |                                                                     |
# | * Inverse problem: azimuth and distance from known                  |
# |                     latitudes and longitudes                        |
# | * Direct problem: Latitude and longitude from known                 |
# |                     position, azimuth and distance.                 |
# | * Sample data                                                       |
# | * Excel spreadsheet                                                 |
# |                                                                     |
# | Vincenty's Inverse formulae                                         |
# | Given: latitude and longitude of two points                         |
# |                     (phi1, lembda1 and phi2, lembda2),              |
# | Calculate: the ellipsoidal distance (s) and                         |
# | forward and reverse azimuths between the points (alpha12, alpha21). |
# |                                                                     |
# -----------------------------------------------------------------------
def vinc_dist(f, a, phi1, lembda1, phi2, lembda2):
    """

    Returns the distance between two geographic points on the ellipsoid
    and the forward and reverse azimuths between these points.
    lats, longs and azimuths are in radians, distance in meters

    Returns ( s, alpha12,  alpha21 ) as a tuple

    """

    if (np.absolute(phi2 - phi1) < 1e-8) and (np.absolute(lembda2 - lembda1) < 1e-8):
        return 0.0, 0.0, 0.0

    two_pi = 2.0 * np.pi

    b = a * (1.0 - f)

    TanU1 = (1 - f) * np.tan(phi1)
    TanU2 = (1 - f) * np.tan(phi2)

    U1 = np.arctan(TanU1)
    U2 = np.arctan(TanU2)

    lembda = lembda2 - lembda1
    last_lembda = -4000000.0                # an impossibe value
    omega = lembda

    # Iterate the following equations,
    #  until there is no significant change in lembda

    while (last_lembda < -3000000.0 or lembda != 0 and np.absolute((last_lembda - lembda) / lembda) > 1.0e-9):

        sqr_sin_sigma = np.power( np.cos(U2) * np.sin(lembda), 2) + \
            np.power((np.cos(U1) * np.sin(U2) -
                      np.sin(U1) * np.cos(U2) * np.cos(lembda)), 2)

        Sin_sigma = np.sqrt(sqr_sin_sigma)

        Cos_sigma = np.sin(U1) * np.sin(U2) + np.cos(U1) * \
            np.cos(U2) * np.cos(lembda)

        sigma = np.arctan2(Sin_sigma, Cos_sigma)

        Sin_alpha = np.cos(U1) * np.cos(U2) * np.sin(lembda) / np.sin(sigma)
        if Sin_alpha > 1 and np.allclose(Sin_alpha, 1.0):
            Sin_alpha = 1.0
        elif Sin_alpha < -1 and np.allclose(Sin_alpha, -1.0):
            Sin_alpha = -1.0
        alpha = np.arcsin(Sin_alpha)

        Cos2sigma_m = np.cos(sigma) - (2 * np.sin(U1) *
                                       np.sin(U2) / np.power(np.cos(alpha), 2))

        C = (f / 16) * np.power(np.cos(alpha), 2) * \
            (4 + f * (4 - 3 * np.power(np.cos(alpha), 2)))

        last_lembda = lembda

        lembda = omega + (1 - C) * f * np.sin(alpha) * (sigma + C * np.sin(sigma) *
                                                        (Cos2sigma_m + C * np.cos(sigma) * (-1 + 2 * np.power(Cos2sigma_m, 2))))

    u2 = np.power(np.cos(alpha), 2) * (a * a - b * b) / (b * b)

    A = 1 + (u2 / 16384) * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))

    B = (u2 / 1024) * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))

    delta_sigma = B * Sin_sigma * (Cos2sigma_m + (B / 4) *
                                   (Cos_sigma * (-1 + 2 * np.power(Cos2sigma_m, 2)) -
                                    (B / 6) * Cos2sigma_m * (-3 + 4 * sqr_sin_sigma) *
                                    (-3 + 4 * np.power(Cos2sigma_m, 2))))

    s = b * A * (sigma - delta_sigma)

    alpha12 = np.arctan2((np.cos(U2) * np.sin(lembda)),
                         (np.cos(U1) * np.sin(U2) - np.sin(U1) * np.cos(U2) * np.cos(lembda)))

    alpha21 = np.arctan2((np.cos(U1) * np.sin(lembda)),
                         (-np.sin(U1) * np.cos(U2) + np.cos(U1) * np.sin(U2) * np.cos(lembda)))

    if (alpha12 < 0.0):
        alpha12 = alpha12 + two_pi
    if (alpha12 > two_pi):
        alpha12 = alpha12 - two_pi

    alpha21 = alpha21 + two_pi / 2.0
    if (alpha21 < 0.0):
        alpha21 = alpha21 + two_pi
    if (alpha21 > two_pi):
        alpha21 = alpha21 - two_pi

    return s, alpha12, alpha21


# ----------------------------------------------------------------------------
# | Vincenty's Direct formulae                                               |
# | Given: latitude and longitude of a point (phi1, lembda1) and             |
# | the geodetic azimuth (alpha12)                                           |
# | and ellipsoidal distance in metres (s) to a second point,                |
# |                                                                          |
# | Calculate: the latitude and longitude of the second point (phi2, lembda2)|
# | and the reverse azimuth (alpha21).                                       |
# |                                                                          |
# ----------------------------------------------------------------------------
def vinc_pt(f, a, phi1, lembda1, alpha12, s):
    """

    Returns: lat and long of projected point and reverse azimuth,
    given a reference point and a distance and azimuth to project.
    lats, longs and azimuths are passed in RADIANS

    Returns ( phi2,  lambda2,  alpha21 ) as a tuple, all in radians

    """

    two_pi = 2.0 * np.pi

    if (alpha12 < 0.0):
        alpha12 = alpha12 + two_pi
    if (alpha12 > two_pi):
        alpha12 = alpha12 - two_pi

    b = a * (1.0 - f)

    TanU1 = (1 - f) * np.tan(phi1)
    U1 = np.arctan(TanU1)
    sigma1 = np.arctan2(TanU1, np.cos(alpha12))
    Sinalpha = np.cos(U1) * np.sin(alpha12)
    cosalpha_sq = 1.0 - Sinalpha * Sinalpha

    u2 = cosalpha_sq * (a * a - b * b) / (b * b)
    A = 1.0 + (u2 / 16384) * (4096 + u2 * (-768 + u2 *
                                           (320 - 175 * u2)))
    B = (u2 / 1024) * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))

    # Starting with the approximation
    sigma = (s / (b * A))

    # Not moving anywhere. We can return the location that was passed in.
    if sigma == 0:
        return phi1, lembda1, alpha12

    last_sigma = 2.0 * sigma + 2.0  # something impossible

    # Iterate the following three equations
    # until there is no significant change in sigma

    # two_sigma_m , delta_sigma

    while (abs((last_sigma - sigma) / sigma) > 1.0e-9):

        two_sigma_m = 2 * sigma1 + sigma

        delta_sigma = B * np.sin(sigma) * (np.cos(two_sigma_m) +
                                           (B / 4) * (np.cos(sigma) *
                                                      (-1 + 2 * np.power(np.cos(two_sigma_m), 2) -
                                                       (B / 6) * np.cos(two_sigma_m) *
                                                       (-3 + 4 * np.power(np.sin(sigma), 2)) *
                                                       (-3 + 4 * np.power( np.cos(two_sigma_m), 2 ))))) \

        last_sigma = sigma
        sigma = (s / (b * A)) + delta_sigma

    phi2 = np.arctan2((np.sin(U1) * np.cos(sigma) + np.cos(U1) * np.sin(sigma) * np.cos(alpha12)),
                      ((1 - f) * np.sqrt(np.power(Sinalpha, 2) +
                                         np.power(np.sin(U1) * np.sin(sigma) - np.cos(U1) * np.cos(sigma) * np.cos(alpha12), 2))))

    lembda = np.arctan2((np.sin(sigma) * np.sin(alpha12)), (np.cos(U1) * np.cos(sigma) -
                                                            np.sin(U1) * np.sin(sigma) * np.cos(alpha12)))

    C = (f / 16) * cosalpha_sq * (4 + f * (4 - 3 * cosalpha_sq))

    omega = lembda - (1 - C) * f * Sinalpha *  \
        (sigma + C * np.sin(sigma) * (np.cos(two_sigma_m) +
                                      C * np.cos(sigma) * (-1 + 2 * np.power(np.cos(two_sigma_m), 2))))

    lembda2 = lembda1 + omega

    alpha21 = np.arctan2(Sinalpha, (-np.sin(U1) * np.sin(sigma) +
                                    np.cos(U1) * np.cos(sigma) * np.cos(alpha12)))

    alpha21 = alpha21 + two_pi / 2.0
    if (alpha21 < 0.0):
        alpha21 = alpha21 + two_pi
    if (alpha21 > two_pi):
        alpha21 = alpha21 - two_pi

    return phi2, lembda2, alpha21
