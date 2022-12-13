#  Known issues and workarounds

PyVO is an open development, Astropy-affiliated package that is still under development.
The VO services themselves are each dependent on their own institutional
implementations, which can and do vary.  There are therefore sometimes minor incompatibilities,
and occasionally major ones.  Those we have run into, we document here along with any workarounds
we find.  But one benefit of the VO is that there may be other services offering the same data with
a different implementation.  So if a given service is not working for you, try going back to 
the registry to see if there might be another.



##  PyVO regsearch() update:  

PyVO's registry search functions have been updated to allow for more
powerful methods of data discovery.  Previously you could
use arguments keywords, servicetype, and waveband, and these still work:
```
image_services = vo.regsearch(servicetype='image', keywords=['sloan vla'])
```
This searches for the strings 'sloan' AND 'vla' in the same entry.  If you instead used ``keywords=['sloan','vla']``,
it would return records with either string, not only both.

But you
can also specify more accurate search criteria using new PyVO Registry
methods.  You can now also search for particular information in a
catalog by its UCD or from a particular source by it's IVOID.  For
some services, you can also search for catalogs with a specified 
spatial, spectral, or temporal coverage.  (Just a warning about this: in some cases,
catalogs are registered as "all sky"  even if they do not 
necessarily have data in any arbitrary direction.) 

Some experimentation may be required to isolate what you want.  For
the latest documentation of the Registry searching, see
[its documentation](https://pyvo.readthedocs.io/en/latest/registry/index.html).  


## Indexing and slicing registry results

```
services=vo.regsearch(servicetype='image')
```

returns a RegistryResults object.  This works like a list in that

```
services[0].search(...)
```
sends a query to the first service, and for easier browsing of the results, you can use an Astropy table:

```
services.to_table()[0]['short_name', 'ivoid', 'access_url']
```

but this doesn't give you something callable.  It gives you an Astropy table, not a PyVO object with a search() method.  

**Workaround**:  To select from a list of results a service whose short_name matches, e.g., 'GALEX', the easiest way is

```
service=[s for s in services if 'GALEX' in s.short_name][0]
```
which assumes that the first match is the right one.  This also works for a few other attributes set for each service such as ivoid, res_description, res_title.   The result is then callable as
```
service.search(...)
```


##  Table descriptions

Getting the descriptions of the tables available for a TAP service may not return useful information
in some cases. For other services, the tables metadata is not being parsed correctly,
another issue we are working on.  

**Workaround**:

This part of data discovery is often still a hands-on task based, for example, on the registry:

[https://vao.stsci.edu/keyword-search/?utf8=✓&search_field=all_fields&q=abellzcat](https://vao.stsci.edu/keyword-search/?utf8=✓&search_field=all_fields&q=abellzcat])


## Galex service from STScI doesn't take format specification:

```
galex_image_services = vo.regsearch(keywords=['galex'], servicetype='image')[0].search(pos=[0,0], size=0.1)
```

produces lots. But

```
galex_image_services = vo.regsearch(keywords=['galex'], servicetype='image')[0].search(pos=[0,0],
    size=0.1, format='image/fits')
```

or 'image/jpeg' produces nothing.

**Workaround**:  Don't limit the format and select after the fact.



##  Some services do not like PyVO's specification of some parameters

For example,

```
services = vo.regsearch(servicetype='image', keywords=['sloan'], waveband='optical')

jhu_dr7_service = [s for s in services if ('SDSSDR7' in s.short_name) and ('jhu' in s.ivoid)][0]

sdss_table = jhu_dr7_service.search(pos=coords, size=0.1, format='image/jpeg')
```

will throw an error because the service URL has a format hard-wired.  If you ask for another format, it will error.  Or if you specify no format whatsoever, then PyVO will add (silently) *format='all'*, which will then error.

**Workaround**:

We do not currently have a workaround for this, since our previous
workaround (specifying format='') no longer works.  TBD.  


## pyvo.dal.ssa.SSARecord.make_dataset_filename() writes suffix  'None'

If you use this function to make a file name, the result for a FITS file has suffix ".None" instead of of ".fits".

**Workaround**:  Name it yourself.  


## Geometric functions in TAP services

Different TAP services have different implementations of the geometric functions in ADQL (See [the ADQL standard](http://www.ivoa.net/documents/latest/ADQL.html).)  These don't always work.  Circles usually do, intersects and polygons sometimes do not.  Not all services support regions.  

**Workaround**:  Various.  Find a different service that provides the same table and try the query there.  Use simpler queries where possible. 



## Asynchronous TAP queries

Each service implements TAP queries differently, whether synchronous
or asynchronous.  The latter option is more powerful and therefore
more complicated.  It is intended for longer queries so that the
connection does not have to remain open waiting for the response.
Because of this, some services limit the sizes of sync queries so that
the do not run too long.  In other words, it will return a truncated
result.  On the other hand, sometimes async services run into issues,
simply because there are more possible things to go wrong.  

**Workaround**: If you run into issues with an asynchronous query, e.g., by using

```
tap_services[0].service.run_async(query)
```

then switch to a synchronous query using

```
tap_services[0].search(query)
```

(which behind the scenes is

```
tap_services[0].service.run_sync(query)
```

exposed at the top level with the search() method.)  

But keep in mind that you may not be getting all results if they
exceed the default maximum returned by a sync query.  Contact the
service administrators to let them know of the problem with the async service.

Note also that if your query contains syntax errors, these are exposed more readily when you use a synchronous search.


## Using UCDs (unified content descriptors)

UCDs are a very useful way to programmatically access the columns you need in tables where they may be named differently.  They can have multiple components separated by a ';' (compound UCDs), and there can be multiple columns tagged with a UCD like "pos.eq.ra" in addition to other UCDs.  The user will still need to understand the different columns to select the one that they want, which may, for example, be "pos.eq.ra;meta.main".  

But note that this complexity is currently not supported by the PyVO getbyucd() or fieldname_with_ucd() methods.  Note that currently they check only the first UCD and will miss any subsequent matches.  

Furthermore, the defintion of UCDs (http://www.ivoa.net/documents/latest/UCD.html) defines the syntax as 'words' separated by semicolons, where the words consist of 'atoms' separated by periods.  The UCD for a Right Ascension column is therefore usually 'pos.eq.ra'.  But the definition of a Simple Cone Search (http://www.ivoa.net/documents/latest/ConeSearch.html) requires that the field used for the position be "POS_EQ_RA_MAIN".
