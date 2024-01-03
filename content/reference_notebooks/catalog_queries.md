---
anaconda-cloud: {}
jupytext:
  notebook_metadata_filter: all
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
language_info:
  codemirror_mode:
    name: ipython
    version: 3
  file_extension: .py
  mimetype: text/x-python
  name: python
  nbconvert_exporter: python
  pygments_lexer: ipython3
  version: 3.11.7
toc:
  base_numbering: 1
  nav_menu: {}
  number_sections: false
  sideBar: true
  skip_h1_title: false
  title_cell: Table of Contents
  title_sidebar: Contents
  toc_cell: false
  toc_position:
    height: calc(100% - 180px)
    left: 10px
    top: 150px
    width: 345.6px
  toc_section_display: true
  toc_window_display: true
widgets:
  state: {}
  version: 1.1.1
---

# Catalog Queries

There are two ways to access astronomical data catalogs that are provided as table data with a VO API.

First, there is a __[Simple Cone Search (SCS) protocol](http://www.ivoa.net/documents/latest/ConeSearch.html)__  used to search a given table with a given position and radius, getting back a table of results.  The interface requires only a position and search radius.

For more complicated searches, the __[Table Access Protocol](http://www.ivoa.net/documents/TAP/)__ (TAP) protocol is  a powerful tool to search any VO table.  Here, we expand on its usage and that of the __[Astronomical Data Query Language](http://www.ivoa.net/documents/latest/ADQL.html)__ (ADQL) that it uses.

- [Catalog Queries](#catalog-queries)
  - [1. Simple cone search](#1-simple-cone-search)
  - [2. Table Access Protocol queries](#2-table-access-protocol-queries)
    - [2.1 TAP services](#21-tap-services)
    - [2.2 Expressing queries in ADQL](#22-expressing-queries-in-adql)
    - [2.3 A use case](#23-a-use-case)
    - [2.4 TAP examples for a given service](#24-tap-examples-for-a-given-service)
  - [3. Using the TAP to cross-correlate and combine](#3-using-the-tap-to-cross-correlate-and-combine)
    - [3.1 Cross-correlating to combine catalogs](#31-cross-correlating-to-combine-catalogs)
    - [3.2 Cross-correlating with user-defined columns](#32-cross-correlating-with-user-defined-columns)
  - [4. Synchronous versus asynchronous queries](#4-synchronous-versus-asynchronous-queries)

```{code-cell} ipython3
# suppress some specific warnings that are not important
import warnings
warnings.filterwarnings("ignore", module="astropy.io.votable.*")
warnings.filterwarnings("ignore", module="pyvo.utils.xml.*")

import io
import numpy as np

# Astropy imports
import astropy.units as u
import astropy.constants as const
from astropy.coordinates import SkyCoord
from astropy.cosmology import Planck15
from astropy.io import votable as apvot
import scipy.integrate

## Generic VO access routines
import pyvo as vo
```

## 1. Simple cone search

+++

Starting with a single simple source first:

```{code-cell} ipython3
coord = SkyCoord.from_name("m51")
print(coord)
```

Below, we go through the exercise of how we can figure out the most relevant table. But for now, let's assume that we know that we want the CFA redshift catalog refered to as 'zcat'. VO services are listed in a central Registry that can be searched through a [web interface](http://vao.stsci.edu/keyword-search/) or using PyVO's `regsearch`.  We use the registry to find the corresponding cone service and then submit our cone search.

Registry services are of the following type:

- simple cone search:  "scs"
- table access protocol:  "tap" or "table"
- simple image search:  "sia" or "image"
- simple spectral access: "ssa"

There are a number of things in the registry related to 'zcat' so we find the specific one that we want, which is the CFA version:

```{code-cell} ipython3
services = vo.regsearch(servicetype='scs', keywords=['zcat'])
services.to_table()['ivoid', 'short_name', 'res_title']
```

Supposing that we want the table with the short_name CFAZ, and we want to retrieve the data for all sources within an arcminute of our specified location:

```{code-cell} ipython3
## Use the one that's CFAZ.
##  Use list comprehension to check each service's short_name attribute and use the first.
cfaz_cone_service = [s for s in services if 'CFAZ' in s.short_name][0]

## We are searching for sources within 10 arcminutes of M51.
results = cfaz_cone_service.search(pos=coord, radius=10*u.arcmin)
results.to_table()
```

The SCS is quite straightforward and returns all of the columns of the given table (which can be anything) for the sources in the region queried.

+++

## 2. Table Access Protocol queries

A TAP query is the most powerful way to search a catalog. A Simple Cone Search only allows you to ask for a position and radius, but TAP allows you to do much more, since the available tables contain much more information.

+++

### 2.1 TAP services

Many services list a single TAP service in the Registry that can access many catalogs, boosting your efficiency, and letting you add constraints based on any column. This is the power of the TAP!

Suppose for our example, we want to select bright galaxy candidates but don't know the coordinates. Therefore, we start from figuring out the best table to query.

+++

As before, we use the `vo.regsearch()` for a servicetype 'tap'.  There are a lot of TAP services in the registry, but they are listed slightly differently than cone services.  The metadata on each catalog is usually published in the registry with its cone service, and then the full TAP service is listed as an "auxiliary" service.  So to find a TAP service for a given catalog, we need to add the option *includeaux=True*. Alternatively, you can start with a single TAP service and then ask it specifically which tables it serves, but for this use case, that is less efficient.

We'll first do a registry search for all auxiliary TAP services related to the "CfA" and "redshift".

```{code-cell} ipython3
tap_services = vo.regsearch(servicetype='tap', keywords=['cfa redshift'], includeaux=True)
tap_services.to_table()['ivoid', 'short_name', 'res_title']
```

There are many tables that mention these keywords. Pick some likely looking ones and look at the descriptions:

```{code-cell} ipython3
for t in tap_services:
    if "cfa" in t.res_title.lower() and "magnitude" in t.res_description.lower():
        print(f"{t.ivoid}:  {t.res_description}\n")
```

From the above information, you can choose the table you want and then use the specified TAP service to query it as described below.

But first we'll look at the other way of finding tables to query with TAP:  by starting with the TAP services listed individually in the Registry.  We see above that the HEASARC has the ZCAT, so what else does it have?

+++

You can find out which tables a TAP serves and then look at the tables descriptions. The last line here sends a query directly to the service to ask it for a list of tables.  (This can take a minute, since there may be a lot of tables.)

```{code-cell} ipython3
#  Here, we're looking for a specific service, and we don't need the includeaux option:
tap_services = vo.regsearch(servicetype='tap',keywords=['heasarc'])
heasarc = tap_services[0]
heasarc_tables=heasarc.service.tables
```

Then let's look for tables matching the terms we're interested in as above.

```{code-cell} ipython3
for tablename in heasarc_tables.keys():
    description = heasarc_tables[tablename].description
    if description and "redshift" in description.lower():
        heasarc_tables[tablename].describe()
        print("Columns={}".format(sorted([k.name for k in heasarc_tables[tablename].columns ])))
        print("----")
```

There are a number of tables that appear to be useful table for our goal, including the ZCAT,  which contains columns with the information that we need to select a sample of the brightest nearby spiral galaxy candidates.

Now that we know all the possible column information in the zcat catalog, we can do more than query on position (as in a cone search) but also on any other column (e.g., redshift, bmag, morph_type).  The query has to be expressed in a language called __[ADQL](http://www.ivoa.net/documents/latest/ADQL.html)__.

+++

### 2.2 Expressing queries in ADQL

+++

The basics of ADQL:

- *SELECT &#42; FROM my.interesting.catalog as cat...*

says you want all ("&#42;") columns from the catalog called "my.interesting.catalog", which you will refer to in the rest of the query by the more compact name of "cat".

Instead of returning all columns, you can

- *SELECT cat.RA, cat.DEC, cat.bmag from catalog as cat...*

to only return the columns you're interested in. To use multiple catalogs, your query could start, e.g.,

- *SELECT c1.RA,c1.DEC,c2.BMAG FROM catalog1 as c1 natural join catalog2 as c2...*

says that you want to query two catalogs zipped together the "natural" way, i.e., by looking for a common column.

To select only some rows of the catalog based on the value in a column, you can add:

- *WHERE cat.bmag < 14*

says that you want to retrieve only those entries in the catalog whose bmag column has a value less than 14.

You can also append

- *ORDER by cat.bmag*

to return the result sorted ascending by one of the columns, adding *DESC* to the end for descending.

A few special functions in the ADQL allow you to query regions:

- *WHERE contains( point('ICRS', cat.ra, cat.dec), circle('ICRS', 210.5, -6.5, 0.5))=1*

is how you would ask for any catalog entries whose RA,DEC lie within a circular region defined by RA,DEC 210.5,-6.5 and a radius of 0.5 (all in degrees).  The 'ICRS' specifies the coordinate system.

See the ADQL documentation for more.

+++

### 2.3 A use case

Here is a simple ADQL query where we print out the relevant columns for the bright (Bmag <14) sources found within 1 degree of M51 (we will discuss how to define the table and column names below):

```{code-cell} ipython3
##  Inside the format call, the {} are replaced by the given variables in order.
##  So this asks for
##  rows of public.zcat where that row's ra and dec (cat.ra and cat.dec from the catalog)
##  are within radius 1deg of the given RA and DEC we got above for M51
##  (coord.ra.deg and coord.dec.deg from our variables defined above), and where
##  the bmag column is less than 14.
query = """SELECT ra, dec, Radial_Velocity, radial_velocity_error, bmag, morph_type FROM public.zcat as cat where
    contains(point('ICRS',cat.ra,cat.dec),circle('ICRS',{},{},1.0))=1 and
    cat.bmag < 14
    order by cat.radial_velocity_error
    """.format(coord.ra.deg, coord.dec.deg)
```

```{code-cell} ipython3
results=heasarc.service.run_async(query)
#results = heasarc.search(query)
results.to_table()
```

See the __[information on the zcat](https://heasarc.gsfc.nasa.gov/W3Browse/galaxy-catalog/zcat.html)__ for column information. (We will use the 'radial_velocity' column rather than the 'redshift' column.) We note that spiral galaxies have morph_type between 1 - 9.

+++

Therefore, we can generalize the query above to complete our exercise and select the brightest (bmag < 14), nearby (radial velocity < 3000), spiral ( morph_type = 1 - 9) galaxies as follows:

```{code-cell} ipython3
query = """SELECT ra, dec, Radial_Velocity, radial_velocity_error, bmag, morph_type FROM public.zcat as cat where
    cat.bmag < 14 and cat.morph_type between 1 and 9 and cat.Radial_Velocity < 3000
    order by cat.Radial_velocity
    """.format(coord.ra.deg, coord.dec.deg)
```

```{code-cell} ipython3
results = heasarc.service.run_async(query)
#results = heasarc.search(query)
results.to_table()
```

### 2.4 TAP examples for a given service

Each service may also provide some example queries.  If they do, then you can see them with, e.g.:

```{code-cell} ipython3
heasarc.service.examples[0]
```

Above, these examples look like a list of dictionaries.  But they are actually a list of objects that can be executed:

```{code-cell} ipython3
for example in heasarc.service.examples:
    print(example['QUERY'])
    result=example.execute()
    #  Stop at one
    break
result.to_table()
```

## 3. Using the TAP to cross-correlate and combine

+++

### 3.1 Cross-correlating to combine catalogs

TAP can also be a powerful way to collect a lot of useful information from existing catalogs in one quick step. For this exercise, we will start with a list of sources, uploaded from our own table, and do a 'cross-correlation' with the *zcat* table.

For more on creating and working with VO tables, see that [notebook](votables.md).  Here, we just read one in that's already prepared:

First, check that this service can handle uploaded tables.   Not all do.

```{code-cell} ipython3
heasarc.service.upload_methods
```

The inline method is what PyVO will use.  These take a while, i.e. half a minute.

```{code-cell} ipython3
query="""
    SELECT cat.ra, cat.dec, Radial_Velocity, bmag, morph_type
    FROM zcat cat, tap_upload.mysources mt
    WHERE
    contains(point('ICRS',cat.ra,cat.dec),circle('ICRS',mt.ra,mt.dec,0.01))=1
    and Radial_Velocity > 0
    ORDER by cat.ra"""
zcattable = heasarc.service.run_async(query, uploads={'mysources': 'data/my_sources.xml'})
#zcattable = heasarc.search(query, uploads={'mysources': 'data/my_sources.xml'})
mytable = zcattable.to_table()
mytable
```

Therefore we now have the Bmag, morphological type and radial velocities for all the sources in our list with a single TAP query.

+++

### 3.2 Cross-correlating with user-defined columns

Our input list of sources contains galaxy pair candidates that may be interacting with each other. Therefore it would be interesting to know what the morphological type and the Bmagnitude are for the potential companions.

In this advanced example, we want our search to be physically motivated since the criterion for galaxy interaction depends on the physical separation of the galaxies. Unlike the previous case, the search radius is not a constant, but varies for each candidate by the distance to the source. Specifically, we want to search for companions that are within 50 kpc of the candidate and therefore first need to find the angular diameter distance that corresponds to galaxy's distance (in our case the radial velocity).

Therefore, we begin by taking our table of objects and adding an angDdeg column:

```{code-cell} ipython3
## The column 'radial_velocity' is c*z but doesn't include the unit; it is km/s
## Get the speed of light from astropy.constants and express in km/s
c = const.c.to(u.km/u.s).value
redshifts = mytable['radial_velocity']/c
mytable['redshift'] = redshifts
physdist = 0.05*u.Mpc # 50 kpc physical distance

angDdist = Planck15.angular_diameter_distance(mytable['redshift'].data)
angDrad = np.arctan(physdist/angDdist)
mytable['angDdeg'] = angDrad.to(u.deg)
mytable
```

Now we construct and run a query that uses the new angDdeg column in every row search. Note, we also don't want to list the original candidates since we know these are in the catalog and we want rather to find any companions. Therefore, we exclude the match if the radial velocities match exactly.

This time, rather than write the table to disk, we'll keep it in memory and give Tap.query() a "file-like" object using io.BytesIO().  This can take half a minute:

```{code-cell} ipython3
## In memory only, use an IO stream.
vot_obj=io.BytesIO()
apvot.writeto(apvot.from_table(mytable),vot_obj)
## (Reset the "file-like" object to the beginning.)
vot_obj.seek(0)
query="""SELECT mt.ra, mt.dec, cat.ra, cat.dec, cat.Radial_Velocity, cat.morph_type, cat.bmag
    FROM zcat cat, tap_upload.mytable mt
    WHERE
    contains(point('ICRS',cat.ra,cat.dec),circle('ICRS',mt.ra,mt.dec,mt.angDdeg))=1
    and cat.Radial_Velocity > 0 and cat.radial_velocity != mt.radial_velocity
    ORDER by cat.ra"""
#  Currently broken due to a bug.
#mytable2 = heasarc.service.run_async(query, uploads={'mytable':vot_obj})
mytable2 = heasarc.search(query, uploads={'mytable':vot_obj})
vot_obj.close()
mytable2.to_table()
```

Therefore, by adding new information to our original data table, we could cross-correlate with the TAP.  We find that, in our candidate list, there is one true pair of galaxies.

+++

## 4. Synchronous versus asynchronous queries

There is one technical detail about TAP queries that you will need to know.  In the code cells above, there are two commands for sending the query, one of which is commented out.  This is because, with the TAP, there are two ways to send such queries.  The default when you use the `search()` method is to us a synchronous query, which means that the query is sent and the client waits for the response.  For large and complicated queries, this may time out, or you may want to run several in parallel.  So there are other options.

The method `service.run_async()` uses an asynchronous query, which means that the query is sent, and then (under the hood without you needing to do anything), the method checks for a response.  From your point of view, these methods look the same;  PyVO is doing different things under the hood, but the method will not return until it has your result.

You need to know about these two methods for a couple of reasons.  First, some services will limit synchronous queries, i.e. they will not necessarily return *all* the results if there are too many of them.  An asynchronous query should have no such restrictions.  In the case of the HEASARC service that we use above, it does not matter, but you should be aware of this and be in the habit of using the asynchronous queries for complete results after an initial interactive exploration.

The second reason to be aware of this is that asynchronous queries may be queued by the service, and they can take a lot longer if the service is very busy or the job is very large.  (The synchronous option in this case may either time out, or it may return quickly but with incomplete results.)

For very large queries, or for submitting queries in parallel, you may wish to use the `submit_job()`, `wait()`, and `fetch_results()` methods to avoid locking up your Python session.  This is described in the [pyvo documentation](https://pyvo.readthedocs.io/en/latest/dal/index.html#jobs).
