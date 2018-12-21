# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
VO Queries
"""

from astroquery.query import BaseQuery
from astroquery.utils import parse_coordinates
from astropy.coordinates import SkyCoord
from . import utils



class ConeClass(BaseQuery):
    """
    TBD
    """
    def __init__(self):
        super(ConeClass, self).__init__()
        self._TIMEOUT = 60 # seconds to timeout
        self._RETRIES = 3 # total number of times to try

    def query(self, service, coords, radius, verbose=False):
        """Basic cone search query function

        Input coords should be either a single string, a single
        SkyCoord object, or a list. It will then loop over the objects
        in the list, assuming each is a single source. Within the
        _one_cone_search function, it then expects likewise a single
        string, a single SkyCoord object, or list of 2 as an RA,DEC
        pair.

        Input service can be a string URL a single row
        of an astropy Table.

        """

        if type(service) is str:
            service = {"access_url":service}


        if type(coords) is str or isinstance(coords, SkyCoord):
            coords = [coords]
        assert type(coords) is list, """
        ERROR: Give a coordinate object that is a single string,
        a list/tuple (ra,dec), a SkyCoord, or a list of any of the above.
        """

        if type(radius) is not list:
            inradius = [radius]*len(coords)
        else:
            inradius = inradius
            assert len(inradius) == len(coords), 'Please give either single radius or list of radii of same length as coords.'

        # Construct list of dictionaries, each with the parameters needed
        # for the function you're calling in the query_loop:
        params = [{'coords':c, 'radius':inradius[i]} for i, c in enumerate(coords)]

        result_list = utils.query_loop(self._one_cone_search, service=service, params=params, verbose=verbose)
        return result_list


    def _one_cone_search(self, coords, radius, service):
        if (type(coords) is tuple or type(coords) is list) and len(coords) == 2:
            coords = parse_coordinates("{} {}".format(coords[0], coords[1]))
        elif type(coords) is str:
            coords = parse_coordinates(coords)
        else:
            assert isinstance(coords, SkyCoord), "ERROR: cannot parse input coordinates {}".format(coords)

        params = {'RA': coords.ra.deg, 'DEC': coords.dec.deg, 'SR':radius}

        response = utils.try_query(service, get_params=params, timeout=self._TIMEOUT, retries=self._RETRIES)

        return utils.astropy_table_from_votable_response(response)


Cone = ConeClass()
