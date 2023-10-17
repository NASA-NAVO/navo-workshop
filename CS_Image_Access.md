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
  version: 3.9.13
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
  toc_section_display: true
  toc_window_display: true
widgets:
  state: {}
  version: 1.1.1
---

# Searching for and retrieving images

In this notebook, we show how to search for and retrieve images from VO services using the Registry and the __[Simple Image Access](http://www.ivoa.net/documents/SIA/)__ (SIA) protocol.

- [Searching for and retrieving images](#searching-for-and-retrieving-images)
    - [1. Finding SIA resources from the Registry](#1-finding-sia-resources-from-the-registry)
    - [2. Using SIA to retrieve an image](#2-using-sia-to-retrieve-an-image)
    - [3. Viewing the resulting image](#3-viewing-the-resulting-image)
        - [JPG images](#jpg-images)
        - [Fits files](#fits-files)
    - [4. Example of data available through multiple services](#4-example-of-data-available-through-multiple-services)
        - [Using HEASARC](#using-heasarc)
        - [Using SDSS SkyServer](#using-sdss-skyserver)

+++

**\*Note:**  for all of these notebooks, the results depend on real-time queries.  Sometimes there are problems, either because a given service has changed, is undergoing maintenance, or the internet connectivity is having problems, etc.  Always retry a couple of times, come back later and try again, and only then send us the problem report to investigate.

```{code-cell} ipython3
import warnings

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
%matplotlib inline  

import pyvo as vo

from astropy.io import fits
import astropy.coordinates as coord
# For downloading files
from astropy.utils.data import download_file

from IPython.display import Image as ipImage, display

# There are a number of relatively unimportant warnings that show up, so for now, suppress them:
warnings.filterwarnings("ignore", module="astropy.io.votable.*")
warnings.filterwarnings("ignore", module="pyvo.utils.xml.*")
```

## 1. Finding SIA resources from the Registry

First, how do we find out what  services are available?  These are listed in a registry at STScI (__[see here](http://www.ivoa.net/documents/RegTAP/)__).  Our Registry function gives a simple interface for how to search for services.  

Let's search for services providing images in the ultraviolet bands:

```{code-cell} ipython3
uv_services = vo.regsearch(servicetype='image',waveband='uv')
uv_services.to_table()['ivoid','short_name','res_title']
```

This returns an astropy table containing information about the services available.  We can then specify the service we want by using the corresponding row.  We'll repeat the search with additional qualifiers to isolate the row we want (note that in the keyword search the "%" character can be used as a wild card):

```{code-cell} ipython3
uvot_services = vo.regsearch(servicetype='image',waveband='uv',keywords=['swift'])
uvot_services.to_table()['ivoid','short_name','res_title']
```

This shows us that the data we are interested in comes from the HEASARC's SkyView service, but the point of these VO tools is that you don't need to know that ahead of time or indeed to care where it comes from.

+++

## 2. Using SIA to retrieve an image

Now we look for images of our favorite source.  See __[the SIA definition](http://www.ivoa.net/documents/WD/SIA/sia-20040524.html)__ for usage.  In short, you can specify the central position and the size (degrees as one or two floats for the RA, DEC directions).  It is up to the service to determine how to provide this. Optionally, you can limit it to the format you want, e.g., "image/fits" or "image/png" etc.  

What is returned to you is not the image itself but a list of images available and how to access them.  This is easiest shown by example:  

```{code-cell} ipython3
coords = coord.SkyCoord.from_name("m51")

im_table = uvot_services[0].search(pos=coords,size=0.2,format='image/jpeg')
im_table.to_table()
```

Extract the fields you're interested in, e.g., the URLs of the images made by skyview.  Note that specifying as we did SwiftUVOT, we get a number of different images, e.g., UVOT U, V, B, W1, W2, etc.  For each survey, there are two URLs, first the FITS IMAGE and second the JPEG.  

Note that different services will return different column names, but all will have a column giving the URL to access the image.  Though it has different column names in different services, it can always be accessed through the `getdataurl` function.

```{code-cell} ipython3
url = im_table[0].getdataurl()
print(url)
```

## 3. Viewing the resulting image

+++

### JPG images

Since we have asked for JPEG images, we can display an image in python easily by using its URL. Each row of the result has a getdataurl() method, and you can then hand the URL to an image displayer such as IPython.display:

```{code-cell} ipython3
img = ipImage(url=im_table[0].getdataurl())
display(img)
```

### Fits files

Or download the FITS image and display it with imshow, or aplpy.

(This often errors off with a time out message.  Just try it again, possibly a couple of times.)

```{code-cell} ipython3
#  Do the search again asking for FITS
im_table = uvot_services[0].search(pos=coords,size=0.2,format='image/fits')

#  Hand the url of the first result to fits.open()
hdu_list = fits.open(im_table[0].getdataurl())
hdu_list.info()
```

#### Using imshow

```{code-cell} ipython3
plt.imshow(hdu_list[0].data, cmap='gray', origin='lower',vmax=0.1)
```

## 4. Example of data available through multiple services

Suppose we want Sloan DSS data.  A generic query finds us a number of possibilities (note that this doesn't work for keywords=['sdss'];  be flexible and try several search terms):

```{code-cell} ipython3
services = vo.regsearch(servicetype='image', keywords=['sloan'], waveband='optical')
services.to_table()[np.where(np.isin(services.to_table()['short_name'], 'SDSSDR7'))]['ivoid', 'short_name']
```

So one of these is served by SDSS's SkyServer and the other by HEASARC's SkyView.  

+++

### Using HEASARC

```{code-cell} ipython3
heasarc_dr7_service = [s for s in services if 'SDSSDR7' in s.short_name and 'heasarc' in s.ivoid][0]

sdss_table_heasarc = heasarc_dr7_service.search(pos=coords,size=0.2,format='image/fits')
sdss_table_heasarc.to_table()
```

```{code-cell} ipython3
## If you only run this once, you can do it in memory in one line:
##  This fetches the FITS as an astropy.io.fits object in memory
# hdu_list = sdss_table_heasarc[0].getdataobj()
## But if you might run this notebook repeatedly with limited bandwidth, 
##  download it once and cache it.  

#  Get the filter g version
file_name=download_file(sdss_table_heasarc[0].getdataurl(), cache=True, timeout=600)
hdu_list = fits.open(file_name)

plt.imshow(hdu_list[0].data, cmap='gray', origin='lower', vmax=1200, vmin=1010)
```

### Using SDSS SkyServer

```{code-cell} ipython3
jhu_dr7_service = [s for s in services if 'SDSSDR7' in s.short_name and 'jhu' in s.ivoid][0]

# Note: jhu_dr7_service access url has hard-wired "format=image/fits". 
# If you specify anythign else, it errors. If you specify nothing, 
# then the search() method puts "format=all", which errors. So specify "format=None" for now.
sdss_table_jhu=jhu_dr7_service.search(pos=coords,size=0.2, format=None)
sdss_table_jhu.to_table().show_in_notebook(display_length = 5)
```

```{code-cell} ipython3
#  Get the filter g version
file_name=download_file(sdss_table_jhu[1].getdataurl(), cache=True, timeout=600)
hdu_list = fits.open(file_name)

plt.imshow(hdu_list[0].data, cmap='gray', origin='lower',vmax=1200,vmin=1010)
```

It turns out that SkyView is just getting images by using the SIAP internally to get the data from the SDSS service.  The point of the VO protocols is that you don't need to know where the data are coming from.  But they can be processed differently.
