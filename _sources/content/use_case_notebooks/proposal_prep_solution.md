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
  version: 3.9.7
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
widgets:
  state: {}
  version: 1.1.1
---

# Preparing a proposal

The Story: Suppose that you are preparing to write a proposal on NGC1365, aiming to investigate the intriguing black hole spin this galaxy with Chandra grating observations (see: [Monster Blackhole Spin Revealed](https://www.space.com/19980-monster-black-hole-spin-discovery.html)) 

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

## Step 1: Find out what the previously quoted Chandra 2-10 keV flux of the central source is for NGC 1365.  

Hint: Do a Registry search for tables served by the HEASARC (where high energy data are archived) to find potential table with this information

```{code-cell} ipython3
#  This gets all services matching, which should be a list of only one:
tap_services=vo.regsearch(servicetype='table',keywords=['heasarc'])
#  This fetches the list of tables that this service serves:
heasarc_tables=tap_services[0].service.tables
```

Hint: The [Chansngcat](https://heasarc.gsfc.nasa.gov/W3Browse/chandra/chansngcat.html) table is likely the best table.  Create a table with ra, dec, exposure time, and flux (and flux errors) from the public.chansngcat catalog for Chandra observations matched within 0.1 degree.

```{code-cell} ipython3
for tablename in heasarc_tables.keys():
    if "chansng" in tablename:  
        print("Table {} has columns={}\n".format(
            tablename,
            sorted([k.name for k in heasarc_tables[tablename].columns ])))
```

```{code-cell} ipython3
# Get the coordinate for NGC 1365
import astropy.coordinates as coord
pos=coord.SkyCoord.from_name("ngc1365")
```

```{code-cell} ipython3
# Construct a query that will get the ra, dec, exposure time, flux, and flux errors 
#  from this catalog in the region around this source:
query="""SELECT ra, dec, exposure, flux, flux_lower, flux_upper FROM public.chansngcat as cat 
    where contains(point('ICRS',cat.ra,cat.dec),circle('ICRS',{},{},0.1))=1 
    and cat.exposure > 0 order by cat.exposure""".format(pos.ra.deg, pos.dec.deg)
#  Submit the query.  (See the CS_Catalog_queries.md for
#    information about these two search options.)
results=tap_services[0].service.run_async(query)
#results=tap_services[0].search(query)
#  Look at the results
results.to_table()
```

## Step 2: Make Images: 

### Create ultraviolet and X-ray images
Hint: Start by checking what UV image services exist (e.g., GALEX?)

```{code-cell} ipython3
## Note that to browse the columns, use the .to_table() method
uv_services=vo.regsearch(servicetype='image',keywords='galex', waveband='uv')
uv_services.to_table()['ivoid','short_name']
```

The keyword search for 'galex' returned a bunch of things that may have mentioned it, but let's just use the ones that have GALEX as their short name:

```{code-cell} ipython3
uv_services.to_table()[
    np.array(['GALEX' in u.short_name for u in uv_services])
    ]['ivoid', 'short_name']
```

Though using the result as an Astropy Table makes it easier to look at the contents, to call the service itself, we cannot use the row of that table.  You have to use the entry in the service result list itself.  So use the table to browse, but select the list of services itself using the properties that have been defined as attributes such as short_name and ivoid:

```{code-cell} ipython3
galex_stsci=[s for s in uv_services if 'GALEX' in s.short_name and 'stsci' in s.ivoid][0]
galex_heasarc=[s for s in uv_services if 'GALEX' in s.short_name and 'heasarc' in s.ivoid][0]
```

Hint: Next create a UV image for the source 

```{code-cell} ipython3
# Do an image search for NGC 1365 in the UV service found above
im_table_stsci=galex_stsci.search(pos=pos,size=0.1)
im_table_stsci.to_table()
```

```{code-cell} ipython3
#  Let's see what HEASARC offers, and this time limit it to FITS 
#   this option doesn't currently work for STScI's service)
im_table_heasarc=galex_heasarc.search(pos=pos,size=0.1,format='image/fits')
im_table_heasarc.to_table()
```

```{code-cell} ipython3
## If you only run this once, you can do it in memory in one line:
##  This fetches the FITS as an astropy.io.fits object in memory
#dataobj=im_table_heasarc[0].getdataobj()
## But if you might run this notebook repeatedly with limited bandwidth, 
##  download it once and cache it.  
file_name = download_file(im_table_heasarc[0].getdataurl(), cache=True, timeout=600)
dataobj=fits.open(file_name)
print(type(dataobj))
```

```{code-cell} ipython3
# Get the FITS file (which is index 0 for the NUV image or index=2 for the FUV image)
from pylab import figure, cm
from matplotlib.colors import LogNorm
plt.matshow(dataobj[0].data, origin='lower', cmap=cm.gray_r, norm=LogNorm(vmin=0.005, vmax=0.3))
```

Hint: Repeat steps for X-ray image. (Note: Ideally, we would find an image in the Chandra 'cxc' catalog) 

```{code-cell} ipython3
x_services=vo.regsearch(servicetype='image',keywords=['chandra'], waveband='x-ray')
print(x_services.to_table()['short_name','ivoid'])
```

```{code-cell} ipython3
## Do an image search for NGC 1365 in the X-ray CDA service found above
xim_table=x_services[0].search(pos=pos,size=0.2)
## Some of these are FITS and some JPEG.  Look at the columns:
print( xim_table.to_table().columns )
first_fits_image_row = [x for x in xim_table if 'image/fits' in x.format][0] 
```

```{code-cell} ipython3
## Create an image from the first FITS file (index=1) by downloading:
## See above for options
#xhdu_list=first_fits_image_row.getdataobj()
file_name = download_file(first_fits_image_row.getdataurl(), cache=True, timeout=600)
xhdu_list=fits.open(file_name)


plt.imshow(xhdu_list[0].data, origin='lower', cmap='cool', norm=LogNorm(vmin=0.1, vmax=500.))
plt.xlim(460, 560)
plt.ylim(460, 560)
```

## Step 3: Make a spectrum: 

### Find what Chandra spectral observations exist already for this source. 
Hint: try searching for X-ray spectral data tables using the registry query

```{code-cell} ipython3
# Use the TAP protocol to list services that contain X-ray spectral data
xsp_services=vo.regsearch(servicetype='ssa',waveband='x-ray')
xsp_services.to_table()['short_name','ivoid','waveband']
```

Hint 2: Take a look at what data exist for our candidate, NGC 1365.

```{code-cell} ipython3
spec_tables=xsp_services[0].search(pos=pos,radius=0.2,verbose=True)
spec_tables.to_table()
```

Hint 3: Download the data to make a spectrum. Note: you might end here and use Xspec to plot and model the spectrum. Or ... you can also try to take a quick look at the spectrum. 

```{code-cell} ipython3
#  Get it and look at it:
#hdu_list=spec_tables[0].getdataobj()
file_name = download_file(spec_tables[0].getdataurl(), cache=True, timeout=600)
hdu_list=fits.open(file_name)

spectra=hdu_list[1].data
print(spectra.columns)
print(len(spectra))
```

```{code-cell} ipython3
## Or write it to disk
import os
if not os.path.isdir('downloads'):
    os.makedirs("downloads")
fname=spec_tables[0].make_dataset_filename()
#  Known issue where the suffix is incorrect:
fname=fname.replace('None','fits')
with open('downloads/{}'.format(fname),'wb') as outfile:
    outfile.write(spec_tables[0].getdataset().read())
```

Extension: Making a "quick look" spectrum. For our purposes, the 1st order of the HEG grating data would be sufficient.

```{code-cell} ipython3
j=1
for i in range(len(spectra)):
    matplotlib.rcParams['figure.figsize'] = (8, 3)
    if abs(spectra['TG_M'][i]) == 1 and (spectra['TG_PART'][i]) == 1:
        ax=plt.subplot(1,2,j)
        pha = plt.plot( spectra['CHANNEL'][i],spectra['COUNTS'][i])
        ax.set_yscale('log')
        if spectra['TG_PART'][i] == 1:
            instr='HEG'
        ax.set_title("{grating}{order:+d}".format(grating=instr, order=spectra['TG_M'][i]))
        plt.tight_layout()
        j=j+1
```

This can then be analyzed in your favorite spectral analysis tool, e.g., [pyXspec](https://heasarc.gsfc.nasa.gov/xanadu/xspec/python/html/index.html).  (For the winter 2018 AAS workshop, we demonstrated this in a [notebook](https://github.com/NASA-NAVO/aas_workshop_2018/blob/master/heasarc/heasarc_Spectral_Access.md) that you can consult for how to use pyXspec, but the pyXspec documentation will have more information.) 

+++

Congratulations! You have completed this notebook exercise.
