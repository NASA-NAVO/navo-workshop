---
jupytext:
  notebook_metadata_filter: a
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Basic Reference

+++

## 0. Setup

Please make sure your environment is set up according to the [instructions here](https://nasa-navo.github.io/navo-workshop/00_SETUP.html).

+++

## 1. Overview

NASA services can be queried from Python in multiple ways.

* Generic Virtual Observatory (VO) queries.
  * Call sequence is consistent, including for non-NASA resources.
  * Use the [`pyvo` package](https://pyvo.readthedocs.io/en/latest/).
  * [Known issues/caveats](https://github.com/NASA-NAVO/navo-workshop/blob/main/KNOWN_ISSUES.md).
* [Astroquery](https://astroquery.readthedocs.io/en/latest/) interfaces:
  * Call sequences not quite as consistent, but follow similar patterns.
* Ad hoc archive-specific interfaces

## 2. VO Services

This workshop will introduce 4 types of VO queries:

* **VO Registry** - Discover what services are available worldwide
* **Simple Cone Search** - Search for catalog object within a specified cone region
* **Simple Image Access** - Search for image products within a spatial region
* **Simple Spectral Access** - Search for spectral products within a spatial region
* **Table Access** - SQL-like queries to databases

### 2.0 Import Necessary Packages

```{code-cell} ipython3
# Generic VO access routines
import pyvo as vo

# For specifying coordinates and angles
from astropy.coordinates import SkyCoord
from astropy.coordinates import Angle
from astropy import units as u

# For downloading files
from astropy.utils.data import download_file

# Ignore unimportant warnings
import warnings
warnings.filterwarnings('ignore', '.*Unknown element mirrorURL.*', vo.utils.xml.elements.UnknownElementWarning)
```

### 2.1 Look Up Services in VO Registry

Simple example:  Find Simple Cone Search (conesearch) services related to SWIFT.

```{code-cell} ipython3
services = vo.regsearch(servicetype='conesearch', keywords=['swift'])
services
```

#### 2.1.1 Use different arguments/values to modify the simple example

| Argument | Description | Examples |
| :-----: | :----------- | :-------- |
| **servicetype** | Type of service | `conesearch` or `scs` for **Simple Cone Search**<br> `image` or `sia` for **Simple Image Access**<br> `spectrum` or `ssa` for **Simple Spectral Access**<br> `table` or `tap` for **Table Access Protocol**|
| **keyword** | List of one or more keyword(s) to match service's metadata. Both ORs and ANDs may be specified.<br><ul><li>(OR) A list of keywords match a service if **any** of the keywords match the service.</li><li>(AND) If a  keyword contains multiple space-delimited words, **all** the words must match the metadata.</li></ul>| `['galex', 'swift']` matches 'galex' or 'swift'<br>`['hst survey']` matches services mentioning both 'hst' and 'survey' |
| **waveband** | Resulting services have data in the specified waveband(s) | ‘radio’, ‘millimeter’, ‘infrared’, ‘optical’, ‘uv’, ‘euv’, ‘x-ray’ ‘gamma-ray’ |

#### 2.1.2 Inspect the results

##### Using pyvo

Although not lists, `pyvo` results can be iterated over to see each individual result.  The results are specialized based on the type of query, providing access to the important properties of the results.  Some useful accessors with registry results are:

* `short_name` - A short name
* `res_title` - A more descriptive title
* `res_description` - A more verbose description
* `reference_url` - A link for more information
* `ivoid` - A unique identifier for the service.  Gives some indication of what organization is serving the data.

```{code-cell} ipython3
# Print the number of results and the 1st 4 short names and titles.
print(f'Number of results: {len(services)}\n')
for s in list(services)[:4]:  # (Treat services as list to get the subset of rows)
    print(f'{s.short_name} - {s.res_title}')
```

##### Filtering results

Of the services we found, which one(s) have 'stsci.edu' in their unique identifier?

```{code-cell} ipython3
stsci_services = [s for s in services if 'stsci.edu' in s.ivoid]
for s in stsci_services:
    print (f'(STScI): {s.short_name} - {s.res_title}')
```

##### Using astropy

With the `to_table()` method, `pyvo` results can also be converted to Astropy `Table` objects which offer a variety of addional features. See [astropy.table](http://docs.astropy.org/en/stable/table/) for more on working with Astropy Tables.

```{code-cell} ipython3
# Convert to an Astropy Table
services_table = services.to_table()

# Print the column names and display 1st 3 rows with a subset of columns
print(f'\nColumn Names:\n{services_table.colnames}\n')
services_table['short_name', 'res_title', 'res_description'][:3]
```

### 2.2 Cone search

Example:  Find a cone search service for the USNO-B catalog and search it around M51 with a .1 degree radius.  (More inspection could be done on the service list instead of blindly choosing the first service.)

The position (`pos`) is best specified with [SkyCoord](http://docs.astropy.org/en/stable/api/astropy.coordinates.SkyCoord.html) objects.

The size of the region is specified with the `radius` keyword and may be decimal degrees or an Astropy [Angle](http://docs.astropy.org/en/stable/api/astropy.coordinates.Angle.html#astropy.coordinates.Angle).

```{code-cell} ipython3
m51_pos = SkyCoord.from_name("m51")
services = vo.regsearch(servicetype='conesearch', keywords='usno-b')
results = services[0].search(pos=m51_pos, radius=0.1)
# Astropy Table is useful for displaying cone search results.
results.to_table()
```

### 2.3 Image search

Example:  Find an image search service for GALEX, and search it around coordinates 13:37:00.950,-29:51:55.51 (M83) with a radius of .2 degrees.  Download the first file in the results.

#### Find an image service

```{code-cell} ipython3
services = vo.regsearch(servicetype='image', keywords=['galex'])
services.to_table()['ivoid', 'short_name', 'res_title']
```

#### Search one of the services

The first service looks good.  Search it!

For more details on using `SkyCoord`, see [its documentation](http://docs.astropy.org/en/stable/api/astropy.coordinates.SkyCoord.html#astropy.coordinates.SkyCoord)

**NOTE**:  For image searches, the size of the region is defined by the `size` keyword which is more like a diameter than a radius.

```{code-cell} ipython3
m83_pos = SkyCoord('13h37m00.950s -29d51m55.51s')
results = services[1].search(pos=m83_pos, size=.2)

# We can look at the results.
results.to_table()
```

#### Download an image

For the first result, print the file format and download the file. If repeatedly executing this code, add `cache=True` to `download_file()` to prevent repeated downloads.

See [`download_file()` documentation here.](https://docs.astropy.org/en/stable/api/astropy.utils.data.download_file.html#astropy.utils.data.download_file)

```{code-cell} ipython3
print(results[0].format)
file_name = download_file(results[0].getdataurl())
file_name
```

### 2.4 Spectral search

Example:  Find a spectral service for x-ray data.  Query it around Delta Ori with a search **diameter** of 10 arc minutes, and download the first data product.  Note that the results table can be inspected for potentially useful columns.

Spectral search is very similar to image search. In this example, note:

* **`diameter`** defines the size of the search region
* `waveband` used in `regsearch()`
* Astropy `Angle` used to specify radius units other than degrees.

```{code-cell} ipython3
# Search for a spectrum search service that has x-ray data.
services = vo.regsearch(servicetype='spectrum', waveband='x-ray')

# Assuming there are services and the first one is OK...
results = services[0].search(pos=SkyCoord.from_name("Delta Ori"),
                             diameter=Angle(10 * u.arcmin))

# Assuming there are results, download the first file.
print(f'Title: {results[0].title}, Format: {results[0].format}')
file_name = download_file(results[0].getdataurl())
file_name
```

### 2.5 Table search

Example:  Find the HEASARC Table Access Protocol (TAP) service, get some information about the available tables.

```{code-cell} ipython3
:tags: [output_scroll]

services = vo.regsearch(servicetype='tap', keywords=['heasarc'])
print(f'{len(services)} service(s) found.')
# We found only one service.  Print some info about the service and its tables.
print(f'{services[0].describe()}')
tables = services[0].service.tables  # Queries for details of the service's tables
print(f'{len(tables)} tables:')
for t in tables:
    print(f'{t.name:30s} - {t.description}')  # A more succinct option than t.describe()
```

#### Column Information

For any table, we can list the column names and descriptions.

```{code-cell} ipython3
for c in tables['zcat'].columns:
    print(f'{c.name:30s} - {c.description}')
```

#### Perform a Query

Example:  Perform a cone search on the ZCAT catalog at M83 with a 1.0 degree radius.

```{code-cell} ipython3
coord = SkyCoord.from_name("m83")
query = f'''
SELECT ra, dec, Radial_Velocity, radial_velocity_error, bmag, morph_type FROM public.zcat as cat where
contains(point('ICRS',cat.ra,cat.dec),circle('ICRS',{coord.ra.deg},{coord.dec.deg},1.0))=1
'''
results = services[0].service.run_async(query)

results.to_table()
```

## 3. Astroquery

Many archives have Astroquery or Astroquery-compliant modules for data access, including:

* Astroquery
  * [HEASARC Queries (astroquery.heasarc)](https://astroquery.readthedocs.io/en/latest/heasarc/heasarc.html)
  * [HITRAN Queries (astroquery.hitran)](https://astroquery.readthedocs.io/en/latest/hitran/hitran.html)
  * [IRSA Image Server program interface (IBE) Queries (astroquery.ibe)](https://astroquery.readthedocs.io/en/latest/ibe/ibe.html)
  * [IRSA Queries (astroquery.ipac.irsa)](https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa.html)
  * [IRSA Dust Extinction Service Queries (astroquery.ipac.irsa.irsa_dust)](https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa_dust.html)
  * [JPL Spectroscopy Queries (astroquery.jplspec)](https://astroquery.readthedocs.io/en/latest/jplspec/jplspec.html)
  * [MAST Queries (astroquery.mast)](https://astroquery.readthedocs.io/en/latest/mast/mast.html)
  * [NASA ADS Queries (astroquery.nasa_ads)](https://astroquery.readthedocs.io/en/latest/nasa_ads/nasa_ads.html)
  * [NED Queries (astroquery.ipac.ned)](https://astroquery.readthedocs.io/en/latest/ipac/ned/ned.html)
* Astroquery-compliant
  * [KOA Queries (pykoa.koa)](https://koa.ipac.caltech.edu/UserGuide/PyKOA/PyKOA.html)

For more, see <https://astroquery.readthedocs.io/en/latest/>

### 3.1 NED

Example:  Get an Astropy Table containing the objects from paper 2018ApJ...858...62K.  For more on the API, see [astroquery](https://astroquery.readthedocs.io/en/latest/ipac/ned/ned.html)

```{code-cell} ipython3
from astroquery.ipac.ned import Ned
objects_in_paper = Ned.query_refcode('2018ApJ...858...62K')
objects_in_paper
```
