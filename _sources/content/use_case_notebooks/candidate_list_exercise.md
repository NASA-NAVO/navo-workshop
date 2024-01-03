---
jupytext:
  notebook_metadata_filter: all
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
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
  version: 3.8.2
---

# Candidate List Exercise

Ogle et al. (2016) mined the NASA/IPAC Extragalactic Database (NED) to identify a new type of galaxy: Superluminous Spiral Galaxies.

Here's the paper: <https://ui.adsabs.harvard.edu/abs/2016ApJ...817..109O/abstract>

Table 1 lists the positions of these Super Spirals. Based on those positions, let's create multiwavelength cutouts for each super spiral to see what is unique about this new class of objects.

+++

## 1. Import the Python modules we'll be using

```{code-cell} ipython3
# Suppress unimportant warnings.
import warnings
warnings.filterwarnings("ignore", module="astropy.io.votable.*")
warnings.filterwarnings("ignore", module="pyvo.utils.xml.*")
warnings.filterwarnings('ignore', '.*RADECSYS=*', append=True)

import matplotlib.pyplot as plt
import numpy as np

# For downloading files
from astropy.utils.data import download_file

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
import astropy.visualization as vis
from astropy.wcs import WCS
from astroquery.ipac.ned import Ned

import pyvo as vo
```

The next cell prepares the notebook to display our visualizations.

```{code-cell} ipython3
%matplotlib inline
```

## 2. Search NED for objects in this paper

Insert a Code Cell below by clicking on the "Insert" Menu and choosing "Insert Cell Below". Then consult QuickReference.md to figure out how to use astroquery to search NED for all objects in a paper, based on the refcode of the paper. Inspect the resulting astropy table.

```{code-cell} ipython3
#  Hint:  the QuickReference has this example:
#objects_in_paper = Ned.query_refcode('2018ApJ...858...62K')
```

## 3. Filter the NED results

The results from NED will include galaxies, but also other kinds of objects (e.g. galaxy clusters, galaxy groups). Print the 'Type' column to see the full range of classifications and filter the results so that we only keep the galaxies in the list.

```{code-cell} ipython3

```

## 4. Search the NAVO Registry for image resources

The paper selected super spirals using WISE, SDSS, and GALEX images. Search the NAVO registry for all image resources, using the 'service_type' search parameter. How many image resources are currently available?

```{code-cell} ipython3
#  Hint:  the QuickReference has this example:
#  services = vo.regsearch(servicetype='conesearch', keywords=['swift'])
```

## 5. Search the NAVO Registry for image resources that will allow you to search for AllWISE images

There are hundreds of image resources...too many to quickly read through. Try adding the 'keywords' search parameter to your registry search, and find the image resource you would need to search the AllWISE images. Remember from the Known Issues that 'keywords' must be a list.

```{code-cell} ipython3
#  Hint:  the QuickReference has this example:
#  services = vo.regsearch(servicetype='conesearch', keywords=['swift'])
```

## 6. Choose the AllWISE image service that you are interested in

```{code-cell} ipython3

```

## 7. Choose one of the galaxies in the NED list

What is the position of this galaxy?

```{code-cell} ipython3
#  Hint:  the QuickReference has this example:
#  m83_pos = SkyCoord('13h37m00.950s -29d51m55.51s')
```

## 8. Search for a list of AllWISE images that cover this galaxy

How many images are returned? Which are you most interested in?

```{code-cell} ipython3
#  Hint:  the QuickReference has this example:
#results = services[1].search(pos=m83_pos, size=.2)
```

## 9. Use the .to_table() method to view the results as an Astropy table

```{code-cell} ipython3

```

## 10. From the result in 8., select the first record for an image taken in WISE band W1 (3.6 micron)

Hints:

* Loop over records and test on the `.bandpass_id` attribute of each record
* Print the `.title` and `.bandpass_id` of the record you find, to verify it is the right one.

```{code-cell} ipython3

```

## 11. Visualize this AllWISE image

Hint: Locate the galaxy in the image by overplotting a ring centered on the galaxy on the image

```{code-cell} ipython3
#  Hint:  the QuickReference has this example:
#  file_name = download_file(results[0].getdataurl())
#  Hint:  when displaying the fits file play with the vmax value, a
#  vmax value around 10 will display a nice image
```

## 12. Plot a cutout of the AllWISE image, centered on your position

Try a 60 arcsecond cutout.

```{code-cell} ipython3
#  Hint:  using Cutout2D imported above from from astropy.nddata
```

## 13. Try visualizing a cutout of a GALEX image that covers your position

Repeat steps 5, 6, 8 through 12 for GALEX.

```{code-cell} ipython3
:tags: [output_scroll]

# Steps 5 & 6: Search the services found in step 4 for GALEX Sources
# Hint: Choose the GALEX service on STSCI
```

```{code-cell} ipython3
# Steps 8 & 9: Find the images that contain your chosen galaxy
# and display using .to_table()
```

```{code-cell} ipython3
# Step 10: Select one of the images and print the title and relevent
# info. For example you can select an image with an 'enrValue' of 2.35e-07
```

```{code-cell} ipython3
# Step 11: Visualize the image and overplot a ring on the image centered
# on your galaxy. (A very small vmax value around 0.01 is recomended)
```

```{code-cell} ipython3
# Step 12: Use Cutout2D to get a 60 arcsecond cutout
# centered on the galaxy
```

## 14. Try visualizing a cutout of an SDSS image that covers your position

Hints:

* Search the registry using `keywords=['sloan']
* Find the service with a `short_name` of `'SDSS SIAP'`
* From Known Issues, recall that an empty string must be specified to the `format` parameter dues to a bug in the service.
* After obtaining your search results, select r-band images using the `.title` attribute of the records that are returned, since `.bandpass_id` is not populated.

+++

(As a workaround to a bug in the SDSS service, pass `format=''` as an argument to the search() function when using the SDSS service.)

```{code-cell} ipython3
# Search the registery to find a service
```

```{code-cell} ipython3
# Search the SDSS SIAP service for images containing your galaxy
```

```{code-cell} ipython3
# Find an image taken in the r filter
```

```{code-cell} ipython3
# Visualize the image and overplot a ring centered on the galaxy
# Hint: a vmax around 0.01 will produce a nice image
```

```{code-cell} ipython3
# use Cutout2D to get a 60 arcsecond cutout centered on the galaxy
```

## 15. Try looping over all positions and plotting multiwavelength cutouts

Hint: Gather the data in ALLWISE, GALEX, and SDSS for each galaxy and plot as seperate cutouts centered on the galaxy position

+++

Warning: this takes a long time to run!  You can limit it to the first three galaxies only, for example, for testing.

```{code-cell} ipython3

```
