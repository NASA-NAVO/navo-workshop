"""
VO Image Queries
"""
from enum import Enum
from astroquery.query import BaseQuery
from astroquery.utils import parse_coordinates
from astropy.coordinates import SkyCoord
from astropy.table import Table, Row
##  Only for debugging
import traceback 

from . import utils

__all__ = ['Image', 'ImageClass', 'ImageTable']

class ImageClass(BaseQuery):
    """
    TBD
    """
    def __init__(self):
        super(ImageClass, self).__init__()
        self._TIMEOUT = 60 # seconds to timeout
        self._RETRIES = 3 # total number of times to try


    def query(self, service, coords, radius='0.000001', image_format=None, verbose=False):
        """Basic image search query function

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

        image_format = one of the following options: ALL, GRAPHICS,
                    FITS, PNG, JPEG/JPG (default = ALL)

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
        image_result_list = []
        for result in result_list:
            try:
                image_table = ImageTable(result, copy=False)
            except Exception as e:
                image_table = Table()
                image_table.meta=result.meta
                image_result_list.append(image_table)
                print("ERROR parsing result as ImageTable:  {}.\nWARNING:  Setting as empty and appending meta-data".format(e))
                traceback.print_exc()
            image_result_list.append(image_table)

#        for result in result_list:
#            image_table = ImageTable(result, copy=False)
#            image_result_list.append(image_table)

        return image_result_list

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
        return utils.astropy_table_from_votable_response(response)

    def get_column(self, table, mnemonic):
        col = None
        if not isinstance(mnemonic, ImageColumn):
            raise ValueError('mnemonic must be an enumeration member of ImageColumn.')
        elif not isinstance(table, Table):
            raise ValueError('table must be an instance of astropy.Table.')
        else:
            col = utils.find_column_by_ucd(table, mnemonic.value)
        return col

    def get_column_name(self, table, mnemonic):
        name = None
        col = self.get_column(table, mnemonic)
        if col is not None:
            name = col.name
        return name


    def get_image(self, row_or_url,filename=None):
        """Give it a row of a table of Image results, returns either an image (IPython.display.Image) or writes the specified filename."""
        from astroquery.query import BaseQuery
        bq = BaseQuery()
        #import requests
        if type(row_or_url) is ImRow:
            url=row_or_url[ImageColumn.ACCESS_URL]
        elif type(row_or_url) is str:
            url=row_or_url
        else:
            raise ValueError("Please specify a string URL or a row of a table of results.") 

        ##r=requests.get(url,stream=True)
        r=bq._request('GET',url, stream=True)

        if filename is None:
            savename='tmp_image.jpg'
        else:
            savename=filename
        with open(savename,'wb') as f:
            f.write(r.content)
        if filename is not None:
            print("Image written to {}\n".format(filename))
            return 
        else:
            from IPython.display import Image as ipImage
            import os
            im=ipImage(savename)
            os.remove(savename)
            return im 


    def get_fits(self, row_or_url,filename=None):
        """Give it a row of a table of Image results, returns either a FITS HDU list from astropy.io.fits type or writes the specified filename."""
        from astroquery.query import BaseQuery
        bq = BaseQuery()
        ##import requests
        if type(row_or_url) is ImRow:
            url=row_or_url[ImageColumn.ACCESS_URL]
        elif type(row_or_url) is str:
            ## Why doesn't this work?
            url=row_or_url
        else:
            raise ValueError("Please specify a string URL or a row of a table of results.") 

        ##r=requests.get(url,stream=True)
        r=bq._request('GET',url, stream=True)

        if filename is None:
            savename='tmp_image.fits'
        else:
            savename=filename
        with open(savename,'wb') as f:
            f.write(r.content)

        if filename is not None:
            print("FITS image written to {}\n".format(filename))
            return 
        else:
           from astropy.io import fits
           import os
           im=fits.open(savename)
           os.remove(savename)
           return im
           




Image = ImageClass()

class ImageColumn(Enum):

    # Required columns
    TITLE = {'ucd': 'VOX:Image_Title', 'required': True, 'description': '''
    A short (usually one line) description of the image. This should concisely
    describe the image to a user, typically identifying the image source
    (e.g., survey name), object name or field coordinates, bandpass/filter, and so forth.
    '''}
    RA = {'ucd': 'POS_EQ_RA_MAIN', 'required': True, 'description': '''
    ICRS right-ascension of the center of the image.
    '''}
    DEC = {'ucd': 'POS_EQ_DEC_MAIN', 'required': True, 'description': '''
    ICRS declination of the center of the image.
    '''}
    NAXES = {'ucd': 'VOX:Image_Naxes', 'required': True, 'description': '''
    The number of image axes.
    '''}
    NAXIS = {'ucd': 'VOX:Image_Naxis', 'required': True, 'description': '''
    Space-separated list giving the length in pixels of each image axis.
    '''}
    SCALE = {'ucd': 'VOX:Image_Scale', 'required': True, 'description': '''
    Space-separated list giving the scale in degrees per pixel of each image axis.
    '''}
    FORMAT = {'ucd': 'VOX:Image_Format', 'required': True, 'description': '''
    The MIME-type of the object associated with the image product, e.g., "image/fits", "image/jpeg, and so forth.
    '''}
    ACCESS_URL = {'ucd': 'VOX:Image_AccessReference', 'required': True, 'description': '''
    The URL to be used to access or retrieve the image. Since the URL may contain XML
    metacharacters, the URL can be enclosed in an XML CDATA section (<![CDATA[...]]>)
    or otherwise URL encoded (see URI Specification) to escape any embedded metacharacters.
    '''}

    # WCS ("should have")
    PROJECTION = {'ucd': 'VOX:WCS_CoordProjection', 'required': False, 'description': '''
    Three-character code ("TAN", "ARC", "SIN", and so forth) specifying the celestial
    projection, as for FITS WCS.
    '''}
    CRPIX = {'ucd': 'VOX:WCS_CoordRefPixel', 'required': False, 'description': '''
    Space-separate list specifying the image pixel coordinates of the WCS reference pixel.
    This is identical to "CRPIX" in FITS WCS.
    '''}
    CRVAL = {'ucd': 'VOX:WCS_CoordRefValue', 'required': False, 'description': '''
    Space-separated list specifying the world coordinates of the WCS reference pixel.
    This is identical to "CRVAL" in FITS WCS.
    '''}
    CDMATRIX = {'ucd': 'VOX:WCS_CDMatrix', 'required': False, 'description': '''
    Space-separated list specifying the WCS CD matrix. This is identical to the
    "CD" term in FITS WCS, and defines the scale and rotation (among other things)
    of the image. Matrix elements should be ordered as CD[i,j] = [1,1], [1,2], [2,1], [2,2].
    '''}

    # "Should have" columns
    INSTRUMENT = {'ucd': 'INST_ID', 'required': False, 'description': '''
    The instrument or instruments used to make the observation, e.g., WFPC2.
    '''}
    MJD_OBS = {'ucd': 'VOX:Image_MJDateObs', 'required': False, 'description': '''
    The mean modified Julian date of the observation. By "mean" we mean the midpoint
    of the observation in terms of normalized exposure times: this is the "characteristic
    observation time" and is independent of observation duration.
    '''}
    REF_FRAME = {'ucd': 'VOX:STC_CoordRefFrame', 'required': False, 'description': '''
    The coordinate system reference frame, selected from "ICRS", "FK5", "FK4", "ECL", "GAL", and "SGAL".
    '''}
    BANDPASS = {'ucd': 'VOX:BandPass_ID', 'required': False, 'description': '''
    The bandpass by name (e.g., "V", "SDSS_U", "K", "K-Band", etc.).
    '''}
    BANDPASS_UNIT = {'ucd': 'VOX:BandPass_Unit', 'required': False, 'description': '''
    The units used to represent spectral values, selected from "meters", "hertz", and "keV".
    No other units are permitted here; the client application may of course present a wider
    range of units in the user interface.
    '''}
    BANDPASS_REFVAL = {'ucd': 'VOX:BandPass_RefValue', 'required': False, 'description': '''
    The characteristic (reference) frequency, wavelength, or energy for the bandpass model.
    '''}
    BANDPASS_HILIMIT = {'ucd': 'VOX:BandPass_HiLimit', 'required': False, 'description': '''
    The upper limit of the bandpass.
    '''}
    BANDPASS_LOLIMIT = {'ucd': 'VOX:BandPass_LoLimit', 'required': False, 'description': '''
    The lower limit of the bandpass.
    '''}
    PIXFLAGS = {'ucd': 'VOX:Image_PixFlags', 'required': False, 'description': '''
    The type of processing done by the image service to produce an output image pixel.
    The string value should be formed from some combination of the following character codes:
    C -- The image pixels were copied from a source image without change, as when an atlas image or cutout is returned.
    F -- The image pixels were computed by resampling an existing image, e.g., to rescale or reproject the data, and were filtered by an interpolator.
    X -- The image pixels were computed by the service directly from a primary data set hence were not filtered by an interpolator.
    Z -- The image pixels contain valid flux (intensity) values, e.g., if the pixels were resampled a flux-preserving interpolator was used.
    V -- The image pixels contain some unspecified visualization of the data, hence are suitable for display but not for numerical analysis.
    For example, a typical image cutout service would have PixFlags="C", whereas a mosaicing service operating on precomputed images might
    have PixFlags="FZ". A preview page, graphics image, or a pixel mask might have PixFlags="V". An image produced by sampling and
    reprojecting a high energy event list might have PixFlags="X". If not specified, PixFlags="C" is assumed.
    '''}
    FILESIZE = {'ucd': 'VOX:Image_FileSize', 'required': False, 'description': '''
    The actual or estimated size of the encoded image in bytes (not pixels!). This is useful for
    image selection and for optimizing distributed computations.
    '''}


#
# Custom subclass of astropy Table.
#

class ImRow(Row):
    """
    This Row allows column access by ImageColumn UCD values.
    """
    def __getitem__(self, item):
        if isinstance(item, ImageColumn):
            colname = self.table.stdcol_to_colname(item)
            val = None
            if colname is not None:
                try:
                    ## Python 3 only 
                    val = super().__getitem__(colname)
                except:
                    ## Python 2 only
                    val = super(ImRow,self).__getitem__(colname)

            return val
        else:
            try:
                ## Python 3 only 
                return super().__getitem__(item)
            except:
                ## Python 2 only 
                return super(ImRow,self).__getitem__(item)


class ImageTable(Table):
    """
    Custom subclass of astropy.table.Table
    """

    Row = ImRow

    __ucdmap__ = None

#    def __init__(self, table,**kwargs):
#        """ An init that attempts to trap issues and return the meta data for debugging."""
#        try:
#            Table.__init__(self,table,**kwargs)
#            self.table=Table(table,**kwargs)
#        except:
#            print("ERROR parsing input as ImageTable. Setting as an empty table and appending meta-data")
#            self.table=Table()
#            self.table.meta=table.meta


    def __compute_ucd_column__(self, mnemonic):
        col = None
        if not isinstance(mnemonic, ImageColumn):
            raise ValueError('mnemonic must be an enumeration member of ImageColumn.')
        else:
            col = utils.find_column_by_ucd(self, mnemonic.value['ucd'])
        return col

    def __compute_ucd_column_name__(self, mnemonic):
        name = None
        col = self.__compute_ucd_column__(mnemonic)
        if col is not None:
            name = col.name
        return name

    def get_ucdmap(self):
        if not self.__ucdmap__:
            self.__ucdmap__ = {}
            for ucd in ImageColumn:
                colname = self.__compute_ucd_column_name__(ucd)
                self.__ucdmap__[ucd.name] = colname

        return self.__ucdmap__

    def __getitem__(self, item):
        if isinstance(item, ImageColumn):
            colname = self.stdcol_to_colname(item)
            if colname is None:
                return None
            else:
                try:
                    ## Python 3 only 
                    return super().__getitem__(colname)
                except:
                    ## Python 2 only
                    return super(ImageTable,self).__getitem__(colname)
        else:
            try:
                ## Python 3 only 
                return super().__getitem__(item)
            except:
                ## Python 2 only 
                return super(ImageTable,self).__getitem__(item)


    def stdcol_to_colname(self, mnemonic):
        if not isinstance(mnemonic, ImageColumn):
            raise ValueError('mnemonic must be an enumeration member of ImageColumn.')
        else:
            ucdmap = self.get_ucdmap()
            name = ucdmap.get(mnemonic.name)
        return name


    def colname_to_stdcol(self, colname):
        imgcol = None
        if colname not in self.colnames:
            raise ValueError("colname {} is not the name of a column in this table".format(colname))
        else:
            ucdmap = self.get_ucdmap()
            for img, col in ucdmap.items():
                if colname == col:
                    for e in ImageColumn:
                        if e.name == img:
                            imgcol = e

        return imgcol
