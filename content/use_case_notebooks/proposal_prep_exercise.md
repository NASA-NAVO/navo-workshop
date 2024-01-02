---
anaconda-cloud: {}
jupytext:
  notebook_metadata_filter: all
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3
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
  version: 3.7.1
nav_menu: {}
toc:
  base_numbering: 1
  nav_menu: {}
  number_sections: false
  sideBar: true
  skip_h1_title: false
  title_cell: Table of Contents
  title_sidebar: Contents
  toc_cell: false
  toc_position: {}
  toc_section_display: block
  toc_window_display: true
---

# Proposal Preparation Exercise

The Story: Suppose that you are preparing to write a proposal on NGC1365, aiming to investigate the intriguing black hole spin this galaxy with Chandra grating observations (see: <https://www.space.com/19980-monster-black-hole-spin-discovery.html> )

In writing proposals, there are often the same tasks that are required: including finding and analyzing previous observations of the proposal, and creating figures that include, e.g., multiwavelength images and spectrum for the source.

```{code-cell} ipython3
# As a hint, we include the code block for Python modules that you will likely need to import:
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline

# For downloading files
from astropy.utils.data import download_file
from astropy.io import fits

import pyvo as vo

## There are a number of relatively unimportant warnings that
## show up, so for now, suppress them:
import warnings
warnings.filterwarnings("ignore", module="astropy.io.votable.*")
warnings.filterwarnings("ignore", module="pyvo.utils.xml.*")
```

## Step 1: Find out what the previously quoted Chandra 2-10 keV flux of the central source is for NGC 1365

Hint: Do a Registry search for tables served by the HEASARC (where high energy data are archived) to find potential table with this information

```{code-cell} ipython3
#  Start with a Registry query to find table services for the HEASARC.
#   Then get the list of tables that this service serves.
#
#  Hint:  the QuickReference has this example:
#services = vo.regsearch(servicetype='tap', keywords=['heasarc'])
#tables = services[0].service.tables
#
#  Hint2:  the QuickReference also has this example:
#for c in tables['zcat'].columns:
#    print(f'{c.name:30s} - {c.description}')
```

Hint: The Chansngcat ( <https://heasarc.gsfc.nasa.gov/W3Browse/chandra/chansngcat.html> ) table is likely the best table.  Create a table with ra, dec, exposure time, and flux (and flux errors) from the public.chansngcat catalog for Chandra observations matched within 0.1 degree.

```{code-cell} ipython3
# Get the coordinate for NGC 1365 with astropy.
```

```{code-cell} ipython3
# Construct a query that will get the ra, dec, exposure time, flux, and flux errors
#  from this catalog in the region around this source and submit the query.
#  (See the CS_Catalog_queries.md )
#  Hint:  the QuickReference has this example:
#coord = SkyCoord.from_name("m83")
#query = f'''
#SELECT ra, dec, Radial_Velocity, radial_velocity_error, bmag, morph_type FROM public.zcat as cat where
#contains(point('ICRS',cat.ra,cat.dec),circle('ICRS',{coord.ra.deg},{coord.dec.deg},1.0))=1
#'''
#results = services[0].service.run_async(query)
```

## Step 2: Make Images

### Create ultraviolet and X-ray images

Hint: Start by checking what UV image services exist (e.g., GALEX?)

```{code-cell} ipython3
#  Hint:  start with a Registry search for relevant image services
```

The keyword search for 'galex' returned a bunch of things that may have mentioned it, but let's just use the ones that have GALEX as their short name:

```{code-cell} ipython3
#  Filter on the short_name attribute of the list of services
```

Though using the result as an Astropy Table makes it easier to look at the contents, to call the service itself, we cannot use the row of that table.  You have to use the entry in the service result list itself.  So use the table to browse, but select the list of services itself using the properties that have been defined as attributes such as short_name and ivoid:

```{code-cell} ipython3
#  You may find more than one service.  Look at both.
```

Hint: Next create a UV image for the source

```{code-cell} ipython3
# Do an image search for NGC 1365 in the UV services found above
#
#  Hint:  the QuickReference has this example:
#results = services[1].search(pos=m83_pos, size=.2)
```

```{code-cell} ipython3
# Get a FITS file and visualize the image
#
#  Hint:  the QuickReference has this example:
#file_name = download_file(results[0].getdataurl())
```

Hint: Repeat steps for X-ray image. (Note: Ideally, we would find an image in the Chandra 'cxc' catalog)

```{code-cell} ipython3

```

## Step 3: Make a spectrum

### Find what Chandra spectral observations exist already for this source

Hint: try searching for X-ray spectral data tables using the registry query

```{code-cell} ipython3
# Search the Registry to list services that contain X-ray spectral data
```

Hint 2: Take a look at what data exist for our candidate, NGC 1365.

```{code-cell} ipython3

```

Hint 3: Download the data to make a spectrum. Note: you might end here and use Xspec to plot and model the spectrum. Or ... you can also try to take a quick look at the spectrum.

```{code-cell} ipython3
#  Get it and look at it:
```

```{code-cell} ipython3
## Or write it to disk
```

Extension: Making a "quick look" spectrum. For our purposes, the 1st order of the HEG grating data would be sufficient.

```{code-cell} ipython3
#  Hint:  You'll have to look into the details of the spectra.
```

This can then be analyzed in your favorite spectral analysis tool, e.g., [pyXspec](https://heasarc.gsfc.nasa.gov/xanadu/xspec/python/html/index.html).  (For the winter 2018 AAS workshop, we demonstrated this in a [notebook](https://github.com/NASA-NAVO/aas_workshop_2018/blob/master/heasarc/heasarc_Spectral_Access.md) that you can consult for how to use pyXspec, but the pyXspec documentation will have more information.)

+++

Congratulations! You have completed this notebook exercise.
