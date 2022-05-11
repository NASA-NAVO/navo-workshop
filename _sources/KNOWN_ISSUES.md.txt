#  Known issues and workarounds

PyVO is an open development, Astropy-affiliated package that is still under development.
The VO services themselves are each dependent on their own institutional
implementations, which can and do vary.  There are therefore sometimes minor incompatibilities,
and occasionally major ones.  Those we have run into, we document here along with any workarounds
we find.  But one benefit of the VO is that there may be other services offering the same data with
a different implementation.  So if a given service is not working for you, try going back to 
the registry to see if there might be another.



##  PyVO regsearch() keywords argument usage


Note also that each string in the list given to PyVO's regsearch() keywords argument is searched in the subject, description, and title of the resource. 

**Workaround**:   If you want to search for the ivoid/identity, you have to do this after the fact as described below.  

```
image_services = vo.regsearch(servicetype='image', keywords=['sloan'])

sdss_gavo_service = [s for s in image_services if 'gavo' in s.ivoid][0]

sdss_gavo_service.search(query)
```


Furthermore, in the case of the resource subject metadata (not easily accessible through Python), the match is a partial string match.   In the case of the description and title, the special function *ivo_hasword* is used, which is a softer matching not currently well documented.   Some experimentation may be required to isolate what you want.  


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

**Workaround**:  To select a service whose short_name matches, e.g., 'GALEX', the easiest way is

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


##  Binary/byte strings

When converting many pvyo results to Astropy tables, using versions of astropy before v4.1,
string columns are represented as byte strings. This issue has been fixed in astropy 4.1.

**Workaround**:  If using astropy versions before 4.1, use byte strings. For example, use 

```
np.isin(services.to_table()['short_name'], b'GALEX')
```

to match strings in the returned tables.  



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

```
sdss_table = jhu_dr7_service.search(pos=coords, size=0.1, format='')
```

Specifying *format=''* (two single quotes) seems to solve problem.  It is combined with the hard-wired service URL without error, and it stops PyVO from adding format='all' and causing an error.


## pyvo.dal.ssa.SSARecord.make_dataset_filename() writes suffix  'None'

If you use this function to make a file name, the result for a FITS file has suffix ".None" instead of of ".fits".

**Workaround**:  Name it yourself.  


## Geometric functions in TAP services

Different TAP services have different implementations of the geometric functions in ADQL (See [the ADQL standard](http://www.ivoa.net/documents/latest/ADQL.html).)  These don't always work.  Circles usually do, intersects and polygons sometimes do not.  Not all services support regions.  

**Workaround**:  Various.  Find a different service that provides the same table and try the query there.  Use simpler queries where possible. 



## Asynchronous TAP queries

Each service implements TAP queries differently, whether synchronous or asynchronous.  The latter option is more powerful and therefore more complicated.

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

But keep in mind that you may not be getting all results.  Contact the service administrators to let them know of the problem.

If your query contains syntax errors, these are exposed more readily when you use a synchronous search.


## Using UCDs (unified content descriptors)

UCDs are a very useful way to programmatically access the columns you need in tables where they may be named differently.  They can have multiple components separated by a ';' (compound UCDs), and there can be multiple columns tagged with a UCD like "pos.eq.ra" in addition to other UCDs.  The user will still need to understand the different columns to select the one that they want, which may, for example, be "pos.eq.ra;meta.main".  

But note that this complexity is currently not supported by the PyVO getbyucd() or fieldname_with_ucd() methods.  Note that currently they check only the first UCD and will miss any subsequent matches.  

Furthermore, the defintion of UCDs (http://www.ivoa.net/documents/latest/UCD.html) defines the syntax as 'words' separated by semicolons, where the words consist of 'atoms' separated by periods.  The UCD for a Right Ascension column is therefore usually 'pos.eq.ra'.  But the definition of a Simple Cone Search (http://www.ivoa.net/documents/latest/ConeSearch.html) requires that the field used for the position be "POS_EQ_RA_MAIN".
