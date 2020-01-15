#  Known issues and workarounds

PyVO is an open development, Astropy-affiliated package that is still being whipped into shape
for end users.  The VO services themselves are each dependent on their own institutional
implementations, which can and do vary.  There are therefore sometimes minor incompatibilities,
and occasionally major ones.  Those we have run into, we document here along with any workarounds
we find.  But one benefit of the VO is that there may be other services offering the same data with
a different implementation.  So if a given service is not working for you, try going back to 
the registry to see if there might be another.



###  PyVO regsearch() keywords argument usage

If you search

```
vo.regsearch(servicetype='image',keywords='galex')
```

then you will get *all* results matching 'g', 'a', 'l', 'e', *or* 'x'.  

**Workaround**:  To match a string, make it a list of one string.

```
vo.regsearch(servicetype='image',keywords=['galex'])
```

Note also that each string in the list given to PyVO's regsearch() keywords argument is searched in the subject, description, and title of the resource. 

**Workaround**:   If you want to search for the ivoid/identity, you have to do this after the fact, with e.g.,

```
vo.regsearch(servicetype='image',keywords=['sdss'])
for i,service in enumerate(tap_services):
    if b'gavo' in tap_services.table['ivoid'][i]:
        sdss_gavo_service=service
        break
sdss_gavo_service.search(query)
```


Furthermore, in the case of the resource subject metadata (not easily accessible through Python), the match is a partial string match.   In the case of the description and title, the special function *ivo_hasword* is used, which is a softer matching not currently well documented.   Some experimentation may be required to isolate what you want.  


### Indexing and slicing registry results

```
services=vo.regsearch(servicetype='image')
```

returns a RegistryResults object.  This works like a list in that

```
services[0]
```

gives you the first service.  But to do actual table operations like searching for matches in the columns, you have to use its table attribute:

```
services[0].table['short_name']
```

This is fine for browsing.  But to select a service whose short_name matches, e.g., 'GALEX', is annoying.

```
np.isin(uv_services.table['short_name'],b'GALEX')
```

returns the masked column that works in a table.  So you can then print just the rows that correspond to that match with

```
services.table[ np.isin(uv_services.table['short_name'],b'GALEX') ]['ivoid','access_url']
```

for example to look at only those rows and only the two specified columns.  But this result is not *callable* the way a PyVO Results object is callable with a search() method.  To get something callable, currently you *cannot* do 

```
services[ np.where(np.isin(services.table['short_name'],b'GALEX'))[0] ].search(pos=pos,size=size)
```

**Workaround**:  Instead, you have to do something like

```
galex_stsci=services[int(np.where(np.isin(uv_services.table['short_name'],b'GALEX'))[0][0])]
galex_stsci.search(pos=pos,size=size)
```

which is ugly and only works for exact matches between the *short_name* field and the specified (byte)string.  We are hoping to improve this situation, and if you come up with a more elegant solution, please tell us.  For something more flexible but also that requires manual intervention:




###  Table descriptions

Getting the descriptions of the tables available for a TAP service may not return useful information
in many cases.

```
tap_services=vo.regsearch(servicetype='table',keywords=['irsa'])
irsa_tables=tap_services[0].service.tables
irsa_tables['gaia_allwise_best_neighbour'].describe() 
```

This returns `No description` and is something to be fixed in the service.  For other services, the tables meta data is not being parsed correctly, another issue we are working on.  

**Workaround**:

This part of data discovery is often still a hands-on task based, for example, on the registry:

[https://vao.stsci.edu/keyword-search/?utf8=✓&search_field=all_fields&q=abellzcat](https://vao.stsci.edu/keyword-search/?utf8=✓&search_field=all_fields&q=abellzcat])


###  Binary/byte strings

We are aware that PyVO and Astropy Tables have a habit of converting strings to binary, or byte, strings.  We hope to make this easier in future.  

**Workaround**:  Use byte strings, for example, as in 

```
np.isin(services.table['short_name'],b'GALEX')
```

to match strings in the returned tables.  



### Galex service from STScI doesn't take format specification:

```
galex_image_services = vo.regsearch(keywords=['galex'], servicetype='image')[0].search(pos=[0,0],size=0.1)
```

produces lots.  But

```
galex_image_services = vo.regsearch(keywords=['galex'], servicetype='image')[0].search(pos=[0,0],size=0.1,format='image/fits')
```

or 'image/jpeg' produces nothing.

**Workaround**:  Don't limit the format and select after the fact.



###  Some services do not like PyVO's specification of some parameters

E.g.,

```
services=vo.regsearch(servicetype='image',keywords=['sloan'],waveband='optical')
jhu_dr7_service=services[int(np.where(np.isin(services.table['short_name'],b'SDSSDR7'))[0][1])]
sdss_table=jhu_dr7_service.search(pos=coords,size=0.1,format='image/jpeg')
```

will throw an error because the service URL has a format hard-wired.  If you ask for another format, it will error.  Or if you specify no format whatsoever, then PyVO will add (silently) *format='all'*, which will then error.

**Workaround**:

```
sdss_table=jhu_dr7_service.search(pos=coords,size=0.1,format='')
```

Specifying *format=''* (two single quotes) seems to solve problem.  It is combined with the hard-wired service URL without error, and it stops PyVO from adding format='all' and causing an error.


### pyvo.dal.ssa.SSARecord.make_dataset_filename() writes suffix  'None'

If you use this function to make a file name, the result for a FITS file has suffix ".None" instead of of ".fits".

**Workaround**:  Name it yourself.  


### Geometric functions in TAP services

Different TAP services have different implementations of the geometric functions in ADQL (See [the ADQL standard](http://www.ivoa.net/documents/latest/ADQL.html).)  These don't always work.  Circles usually do, intersects and polygons sometimes do not.  Not all services support regions.  

**Workaround**:  Various.  Find a different service that provides the same table and try the query there.  Use simpler queries where possible. 



### Asynchronous TAP queries

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


