# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
VO Queries
"""

from __future__ import print_function, division
#from IPython.core.debugger import Tracer
from astroquery.query import BaseQuery
from astroquery.utils.tap.core import Tap as coreTap
import numpy
from . import utils

__all__ = ['Tap', 'TapClass']

class TapClass(BaseQuery):
    """
    Tap query class.
    """


    def __init__(self):

        super(TapClass, self).__init__()
        self._TIMEOUT = 60 # seconds
        self._RETRIES = 2 # total number of times to try

    def query(self, service, query, upload_file=None,upload_name=None):
        """Prototype of TAP class.  Uploaded file is kludged, as are list_tables and list_columns.  To be finalized."""

        if type(service) is str:
            service = {"access_url":service}

        url = service['access_url'] + '/sync?'

        tap_params = {
            "request": "doQuery",
            "lang": "ADQL",
            "query": query
        }

        if upload_file is not None:
            import requests, io
            if upload_name is None:
                print("ERROR: you have to give upload_name to use in the query for the uploaded table.")
                return None

            ## Why does neither of these work with utils.try_query(files=files....) ?
            #files={'uplt':open(upload_file,'rb')}
            #files={'uplt':upload_file}
            #tap_params['upload'] = upload_name+',param:uplt'

            if type(upload_file) is str:
                files={'uplt':open(upload_file, 'rb')}
            elif type(upload_file) is io.BytesIO:
                files={'uplt':upload_file}
            cc_params={
                'lang': 'ADQL', 
                'request': 'doQuery',
                'upload':'{},param:uplt'.format(upload_name)
                }

            cc_params["query"]=query
            response = requests.post(url,data=cc_params,stream=True,files=files)
            
        else:
            response = utils.try_query(url, post_data=tap_params, timeout=self._TIMEOUT, retries=self._RETRIES)

        aptable = utils.astropy_table_from_votable_response(response)
        return aptable


    def list_tables(self,service_url,contains=None):
        """Uses TapPlus() 'TAP-compatible' function to list tables at a given service"""
        tap_service = coreTap(url=service_url)
        tables=tap_service.load_tables()
        retlist=[]
        for table in (tables):
            tname=table.get_qualified_name()
            if contains is None or (contains is not None and contains in tname):
                print(tname)
                retlist.append(tname)
        return retlist


    def list_columns(self, service_url, tablename):
        """Simple way to get column names by getting 1st row only.  To be done more intelligently."""

        query="select top 1 * from {}".format(tablename) 
        try:
            table=self.query( service_url, query)
            if len(table) > 0:
                return table.columns
            else:
                return table.meta
        except:
            return table.meta


Tap = TapClass()
