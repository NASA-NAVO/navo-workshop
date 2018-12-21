from astroquery.query import BaseQuery
from astroquery.utils import parse_coordinates
from astropy.coordinates import SkyCoord
from astropy.table import Table, Row
from enum import Enum

from . import utils

__all__ = ['Spectra', 'SpectraClass']

class SpectraClass(BaseQuery):
    def __init__(self):
        super(SpectraClass, self).__init__()
        self._TIMEOUT = 60 # seconds to timeout
        self._RETRIES = 3 # total number of times to try


    def query(self, service, coords, radius='0.000001', image_format=None, verbose=False):
        """Basic spectra search query function

        Input coords should be either a single string, a single
        SkyCoord object, or a list. It will then loop over the objects
        in the list, assuming each is a single source. Within the
        _one_image_search function, it then expects likewise a single
        string, a single SkyCoord object, or list of 2 as an RA,DEC
        pair.

        Input service can be a string URL, an astropy Table returned
        from Registry.query() (or selected from it), or a single row
        of an astropy Table. If none is given, the kwargs will be
        passed to a Registry.query() call.

        """

        if type(service) is str:
            service = {"access_url":service}

        if type(coords) is str or isinstance(coords, SkyCoord):
            coords = [coords]
        assert type(coords) is list, "ERROR: Give a coordinate object that is a single string, a list/tuple (ra,dec), a SkyCoord, or a list of any of the above."
#        Tracer()()
        if type(radius) is not list:
            inradius = [radius]*len(coords)
        else:
            inradius = radius
            assert len(inradius) == len(coords), 'Please give either single radius or list of radii of same length as coords.'
        # Passing along proper image format parameters:
        if image_format is not None:
            if "fits" in image_format.lower():
                image_format = "image/fits"
            elif "jpeg" in image_format.lower():
                image_format = "image/jpeg"
            elif "jpg" in image_format.lower():
                image_format = "image/jpeg"
            elif "png" in image_format.lower():
                image_format = "image/png"
            elif "graphics" in image_format.lower():
                image_format = "GRAPHICS"
            elif "all" in image_format.lower():
                image_format = "ALL"
            else:
                raise Exception("ERROR: please give a image_format that is one of FITS, JPEG, PNG, ALL, or GRAPHICS")

        # Expand the input parameters to a list of input parameter dictionaries for the call to query_loop.
        params = [{'coords':c, 'radius':inradius[i], 'image_format':image_format} for i, c in enumerate(coords)]

        result_list = utils.query_loop(self._one_image_search, service=service, params=params, verbose=verbose)
        spectra_result_list = []
        for result in result_list:
            spectra_table = SpectraTable(result, copy=False)
            spectra_result_list.append(spectra_table)

        return spectra_result_list

    def _one_image_search(self, coords, radius, service, image_format=None):
        if (type(coords) is tuple or type(coords) is list) and len(coords) == 2:
            coords = parse_coordinates("{} {}".format(coords[0], coords[1]))
        elif type(coords) is str:
            coords = parse_coordinates(coords)
        else:
            assert isinstance(coords, SkyCoord), "ERROR: cannot parse input coordinates {}".format(coords)

        params = {
            'POS': utils.sval(coords.ra.deg) + ',' + utils.sval(coords.dec.deg),
            'SIZE': utils.sval(2.*float(radius)),   #Note: size in SIA is diameter, not radius!
            }
        if image_format is not None:
            params['FORMAT'] = image_format

        response = utils.try_query(service, get_params=params, timeout=self._TIMEOUT, retries=self._RETRIES)
        #Tracer()()
        return utils.astropy_table_from_votable_response(response)

    def get_column(self, table, mnemonic):
        col = None
        if not isinstance(mnemonic, SpectraColumn):
            raise ValueError('mnemonic must be an enumeration member of SpectraColumn.')
        elif not isinstance(table, Table):
            raise ValueError('table must be an instance of astropy.Table.')
        else:
            col = utils.find_column_by_utype(table, mnemonic.value)
        return col

    def get_column_name(self, table, mnemonic):
        name = None
        col = self.get_column(table, mnemonic)
        if col is not None:
            name = col.name
        return name



    def get_fits(self, row_or_url,filename=None):
        """Give it a row of a table of Spectra results, returns either a FITS HDU list from astropy.io.fits type or writes the specified filename."""
        import requests
        if type(row_or_url) is SpRow:
            url=row_or_url[SpectraColumn.ACCESS_URL]
        elif type(row_or_url) is str:
            ## Why doesn't this work?
            url=row_or_url
        else:
            raise ValueError("Please specify a string URL or a row of a table of results.") 

        r=requests.get(url, stream=True)
        if filename is None:
            savename='tmp_spectrum.fits'
        else:
            savename=filename
        with open(savename,'wb') as f:
            f.write(r.content)

        if filename is not None:
            print("FITS spectrum written to {}\n".format(filename))
            return 
        else:
           from astropy.io import fits
           import os
           spectrum=fits.open(savename)
           os.remove(savename)
           return spectrum
           



Spectra = SpectraClass()

class SpectraColumn(Enum):
    # Required columns
    ACCESS_URL = {'utype': 'ssa:Access.Reference', 'required': True, 'description': '''
    URL used to access the dataset
    '''}
    FORMAT = {'utype': 'ssa:Access.Format', 'required': True, 'description': '''
    MIME type of dataset
    '''}
    TITLE = {'utype': 'ssa:DataID.Title', 'required': True, 'description': '''
    Dataset title
    '''}
    PUBLISHER = {'utype': 'ssa:Curation.Publisher', 'required': True, 'description': '''
    Dataset title
    '''}
    LENGTH = {'utype': 'ssa:Dataset.Length', 'required': True, 'description': '''
    Number of points in spectrum
    '''}
    POSITION = {'utype': 'ssa:Char.SpatialAxis.Coverage.Location.Value', 'required': True, 'description': '''
    Space-separated RA Dec tuple, decimal degrees
    '''}
    EXTENT = {'utype': 'ssa:Char.SpatialAxis.Coverage.Bounds.Extent', 'required': True, 'description': '''
    Aperture angular diameter, degrees
    '''}

    # "Should have" columns
    SIZE = {'utype': 'ssa:Access.Size', 'required': False, 'description': '''
    Estimated (not actual) dataset size
    '''}

    # WCS (also "should have")


#
# Custom subclass of astropy Table.
#

class SpRow(Row):
    """
    This Row allows column access by SpectraColumn utype values.
    """
    def __getitem__(self, item):
        if isinstance(item, SpectraColumn):
            colname = self.table.stdcol_to_colname(item)
            val = None
            if colname is not None:
                try:
                    ## Python 3 only 
                    val = super().__getitem__(colname)
                except:
                    ## Python 2 only
                    val = super(SpRow,self).__getitem__(colname)

                return val
        else:
            try:
                ## Python 3 only 
                return super().__getitem__(item)
            except:
                ## Python 2 only 
                return super(SpRow,self).__getitem__(item)
            #return super().__getitem__(item)


class SpectraTable(Table):
    """
    Custom subclass of astropy.table.Table
    """

    Row = SpRow

    __utypemap__ = None


    def __compute_utype_column__(self, mnemonic):
        col = None
        if not isinstance(mnemonic, SpectraColumn):
            raise ValueError('mnemonic must be an enumeration member of SpectraColumn.')
        else:
            col = utils.find_column_by_utype(self, mnemonic.value['utype'])
        return col

    def __compute_utype_column_name__(self, mnemonic):
        name = None
        col = self.__compute_utype_column__(mnemonic)
        if col is not None:
            name = col.name
        return name

    def get_utypemap(self):
        if not self.__utypemap__:
            self.__utypemap__ = {}
            for utype in SpectraColumn:
                colname = self.__compute_utype_column_name__(utype)
                self.__utypemap__[utype.name] = colname

        return self.__utypemap__

    def __getitem__(self, item):
        if isinstance(item, SpectraColumn):
            colname = self.stdcol_to_colname(item)
            if colname is None:
                return None
            else:
                try:
                    ## Python 3 only 
                    val = super().__getitem__(colname)
                except:
                    ## Python 2 only
                    val = super(SpectraTable,self).__getitem__(colname)
                    #return super().__getitem__(colname)
                return val
        else:
            try:
                ## Python 3 only 
                return super().__getitem__(item)
            except:
                ## Python 2 only 
                return super(SpectraTable,self).__getitem__(item)


    def stdcol_to_colname(self, mnemonic):
        if not isinstance(mnemonic, SpectraColumn):
            raise ValueError('mnemonic must be an enumeration member of SpectraColumn.')
        else:
            utypemap = self.get_utypemap()
            name = utypemap.get(mnemonic.name)
        return name

    def colname_to_stdcol(self, colname):
        imgcol = None
        if colname not in self.colnames:
            raise ValueError("colname {} is not the name of a column in this table.".format(colname))
        else:
            utypemap = self.get_utypemap()
            for img, col in utypemap.items():
                if colname == col:
                    for e in SpectraColumn:
                        if e.name == img:
                            imgcol = e

        return imgcol
