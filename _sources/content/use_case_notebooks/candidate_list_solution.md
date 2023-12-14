---
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
  version: 3.11.6
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

# Science User Case - Inspecting a Candidate List

[Ogle et al. (2016)](https://ui.adsabs.harvard.edu/abs/2016ApJ...817..109O/abstract) mined the NASA/IPAC Extragalactic Database (NED) to identify a new type of galaxy: Superluminous Spiral Galaxies.

Table 1 lists the positions of these Super Spirals. Based on those positions, let's create multiwavelength cutouts for each super spiral to see what is unique about this new class of objects.

+++

## 1. Import the Python modules we'll be using.

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

## 2. Search NED for objects in this paper.

Insert a Code Cell below by clicking on the "Insert" Menu and choosing "Insert Cell Below". Then consult QuickReference.md to figure out how to use astroquery to search NED for all objects in a paper, based on the refcode of the paper. Inspect the resulting astropy table.

```{code-cell} ipython3
:tags: [output_scroll]

objects_in_paper = Ned.query_refcode('2016ApJ...817..109O')
objects_in_paper.show_in_notebook()
```

## 3. Filter the NED results.

The results from NED will include galaxies, but also other kinds of objects (e.g. galaxy clusters, galaxy groups). Print the 'Type' column to see the full range of classifications and filter the results so that we only keep the galaxies in the list.

```{code-cell} ipython3
objects_in_paper['Type']
```

```{code-cell} ipython3
:tags: [output_scroll]

# Keep only the galaxies from the list
galaxies = objects_in_paper[np.array(objects_in_paper['Type']) == 'G']

galaxies.show_in_notebook()
```

## 4. Search the NAVO Registry for image resources.

The paper selected super spirals using WISE, SDSS, and GALEX images. Search the NAVO registry for all image resources, using the 'service_type' search parameter. How many image resources are currently available?

```{code-cell} ipython3
image_services = vo.regsearch(servicetype='image')

print(f'{len(image_services)} result(s) found.')

image_services.to_table()['ivoid', 'short_name', 'res_title']
```

## 5. Search the NAVO Registry for image resources that will allow you to search for AllWISE images.

There are hundreds of image resources...too many to quickly read through. Try adding the 'keywords' search parameter to your registry search, and find the image resource you would need to search the AllWISE images. Remember from the Known Issues that 'keywords' must be a list.

```{code-cell} ipython3
allwise_image_services = vo.regsearch(servicetype='image', keywords=['allwise'])

print(f'{len(allwise_image_services)} result(s) found.')

allwise_image_services.to_table()['ivoid', 'short_name', 'res_title']
```

## 6. Choose the AllWISE image service that you are interested in.

```{code-cell} ipython3
allwise_image_service = allwise_image_services[0]
allwise_image_service.service
```

## 7. Choose one of the galaxies in the NED list.

```{code-cell} ipython3
ra = galaxies['RA'][0]
dec = galaxies['DEC'][0]
pos = SkyCoord(ra, dec, unit = 'deg')
```

```{code-cell} ipython3
ra,dec
```

## 8. Search for a list of AllWISE images that cover this galaxy.

How many images are returned? Which are you most interested in?

```{code-cell} ipython3
allwise_image_table = allwise_image_service.search(pos=pos, size=0)
allwise_image_table
```

## 9. Use the .to_table() method to view the results as an Astropy table.

```{code-cell} ipython3
allwise_images = allwise_image_table.to_table()
allwise_images
```

## 10. From the result in 8., select the first record for an image taken in WISE band W1 (3.6 micron)

Hints:
* Loop over records and test on the `.bandpass_id` attribute of each record
* Print the `.title` and `.bandpass_id` of the record you find, to verify it is the right one.

```{code-cell} ipython3
for allwise_image_record in allwise_image_table:
    if 'W1' in allwise_image_record.bandpass_id:
        break
print(allwise_image_record.title, allwise_image_record.bandpass_id)
```

## 11. Visualize this AllWISE image.

```{code-cell} ipython3
## If you only run this once, you can do it in memory in one line:
##  This fetches the FITS as an astropy.io.fits object in memory
#allwise_w1_image = allwise_image_record.getdataobj()
## But if you might run this notebook repeatedly with limited bandwidth, 
##  download it once and cache it.  
file_name = download_file(allwise_image_record.getdataurl(), cache=True)  
allwise_w1_image = fits.open(file_name)
```

```{code-cell} ipython3
fig = plt.figure()

wcs = WCS(allwise_w1_image[0].header)
ax = fig.add_subplot(1, 1, 1, projection=wcs)
ax.imshow(allwise_w1_image[0].data, cmap='gray_r', origin='lower', vmax = 10)
ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')
```

## 12. Plot a cutout of the AllWISE image, centered on your position.

Try a 60 arcsecond cutout.

```{code-cell} ipython3
size = 60
cutout = Cutout2D(allwise_w1_image[0].data, pos, (size, size), wcs=wcs)
wcs = cutout.wcs

fig = plt.figure()

ax = fig.add_subplot(1, 1, 1, projection=wcs)
ax.imshow(cutout.data, cmap='gray_r', origin='lower', vmax = 10)
ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')
```

## 13. Try visualizing a cutout of a GALEX image that covers your position.

Repeat steps 4, 5, 6, 8 through 12 for GALEX.

```{code-cell} ipython3
galex_image_services = vo.regsearch(keywords=['galex'], servicetype='image')
print(f'{len(galex_image_services)} result(s) found.')
galex_image_services.to_table()['ivoid', 'short_name', 'res_title']
```

```{code-cell} ipython3
galex_image_service = galex_image_services[0]
```

```{code-cell} ipython3
galex_image_table = galex_image_service.search(pos=pos, size=0.0, intersect='covers')
```

```{code-cell} ipython3
for i in range(len(galex_image_table)):
    if (('image/fits' in galex_image_table[i].format) and
        (galex_image_table['energy_bounds_center'][i]==2.35e-07) and
        (galex_image_table[i]['productType'] == 'SCIENCE')):
        break
galex_image_record = galex_image_table[i]
print(galex_image_record.title, galex_image_record.bandpass_id)
```

```{code-cell} ipython3
## See above regarding two ways to do this: 
#galex_nuv_image = fits.open(galex_image_record.getdataurl())
file_name = download_file(galex_image_record.getdataurl(), cache=True)  
galex_nuv_image=fits.open(file_name)
```

```{code-cell} ipython3
image_data = galex_nuv_image[0].data
print('Min:', np.min(image_data))
print('Max:', np.max(image_data))
print('Mean:', np.mean(image_data))
print('Stdev:', np.std(image_data))
```

```{code-cell} ipython3
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection=WCS(galex_nuv_image[0].header))
ax.imshow(galex_nuv_image[0].data, cmap='gray_r', origin='lower', vmin=0.0, vmax=0.01)
ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')   
```

```{code-cell} ipython3
cutout = Cutout2D(galex_nuv_image[0].data, pos, size, wcs=WCS(galex_nuv_image[0].header))

fig = plt.figure()

ax = fig.add_subplot(1, 1, 1, projection=cutout.wcs)
ax.imshow(cutout.data, cmap='gray_r', origin='lower', vmin = 0.0, vmax = 0.01)
ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')
```

## 14. Try visualizing a cutout of an SDSS image that covers your position.

Hints:
* Search the registry using `keywords=['sloan']
* Find the service with a `short_name` of `'SDSS SIAP'`
* After obtaining your search results, select r-band images using the `.title` attribute of the records that are returned, since `.bandpass_id` is not populated.

```{code-cell} ipython3
sdss_image_services = vo.regsearch(keywords=['sloan'], servicetype='image')
sdss_image_services.to_table()['ivoid', 'short_name', 'res_title', 'source_value']
```

```{code-cell} ipython3
#  Use list comprehension to check each service's short_name attribute.
#   Given the above, we know the first match is the right one.  
sdss_image_service = [s for s in sdss_image_services if 'SDSS SIAP' in s.short_name ][0]
sdss_image_service.short_name
```

```{code-cell} ipython3
sdss_image_table = sdss_image_service.search(pos=pos, size=0.0)
len(sdss_image_table['Title'])
```

```{code-cell} ipython3
for sdss_rband_record in sdss_image_table:
    if 'Sloan Digital Sky Survey - Filter r' in sdss_rband_record.title:
        break
print(sdss_rband_record.title, sdss_rband_record.bandpass_id)
```

```{code-cell} ipython3
##  See above regarding two ways to do this
# sdss_rband_image = fits.open(sdss_rband_record.getdataurl())
file_name = download_file(sdss_rband_record.getdataurl(), cache=True)  
sdss_rband_image=fits.open(file_name)
```

```{code-cell} ipython3
fig = plt.figure()

ax = fig.add_subplot(1, 1, 1, projection=WCS(sdss_rband_image[0].header))

interval = vis.PercentileInterval(99.9)
vmin,vmax = interval.get_limits(sdss_rband_image[0].data)
norm = vis.ImageNormalize(vmin=vmin, vmax=vmax, stretch=vis.LogStretch(1000))
ax.imshow(sdss_rband_image[0].data, cmap = 'gray_r', norm = norm, origin = 'lower')          
ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')
```

```{code-cell} ipython3
cutout = Cutout2D(sdss_rband_image[0].data, pos, size, wcs=WCS(sdss_rband_image[0].header))
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection=cutout.wcs)
vmin,vmax = interval.get_limits(sdss_rband_image[0].data)
norm = vis.ImageNormalize(vmin=vmin, vmax=vmax, stretch=vis.LogStretch(1000))
ax.imshow(cutout.data, cmap = 'gray_r', norm = norm, origin = 'lower')          
ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')
```

## 15. Try looping over all positions and plotting multiwavelength cutouts.

+++

Warning: this cell takes a long time to run! We limit it to the first three galaxies only.

```{code-cell} ipython3
# Pick the first 3 galaxies.
galaxy_subset = galaxies[0:3]

# For each galaxy,
for galaxy in galaxy_subset:

    # Establish the position.
    ra = galaxy['RA']
    dec = galaxy['DEC']
    pos = SkyCoord(ra, dec, unit = 'deg')  
    
    # Set up the plot for this position.
    fig = plt.figure(figsize=(20,6))
    plt.suptitle('POSITION = ' + str(ra) + ', ' + str(dec), fontsize=16)

    # GALEX
    
    # Find the GALEX images that overlap the position.
    galex_image_table = galex_image_service.search(pos=pos, size=0.25)
    
    # Find the GALEX All-Sky Image Survey (AIS) Near-UV FITS coadd. 
    galex_image_record = None
    for record in galex_image_table:
        if (('image/fits' in record.format) and
            (record['energy_bounds_center'] == 2.35e-07) and
            (record['productType'] == 'SCIENCE')):
            galex_image_record = record
            break
    
    if galex_image_record is not None:
        # Create a cutout.
        file_name = download_file(galex_image_record.getdataurl(), cache=True)  
        gimage = fits.open(file_name)
        galex_cutout = Cutout2D(gimage[0].data, pos, size, wcs=WCS(gimage[0].header))

        # Plot the cutout in the first position of a 1x3 (rowsxcols) grid.
        ax = fig.add_subplot(1, 3, 1, projection=galex_cutout.wcs)
        ax.set_title(galex_image_record.title)
        ax.imshow(galex_cutout.data, cmap='gray_r', origin='lower', vmin = 0.0, vmax = 0.01)
        ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')
    else:
        # We didn't find a suitable image, so leave that subplot blank.
        ax = fig.add_subplot(1, 3, 1, projection=galex_cutout.wcs)
        ax.set_title('GALEX image not found')
    
    # SDSS
    
    # Find the SDSS images that overlap the position.
    sdss_image_table = sdss_image_service.search(pos=pos, size=0)
    
    # Find the first SDSS r-band image.
    sdss_rband_record = None
    for record in sdss_image_table:
        if 'Sloan Digital Sky Survey - Filter r' in record.title:
            sdss_rband_record = record
            break
    
    if sdss_rband_record is not None:
        # Create a cutout.
        file_name = download_file(sdss_rband_record.getdataurl(), cache=True)  
        sdss_rband_image=fits.open(file_name)

        sdss_cutout = Cutout2D(sdss_rband_image[0].data, pos, size,
                               wcs=WCS(sdss_rband_image[0].header))

        # Plot the cutout in the second position of a 1x3 grid.
        vmin,vmax = interval.get_limits(sdss_cutout.data)
        norm = vis.ImageNormalize(vmin=vmin, vmax=vmax, stretch=vis.LogStretch(1000))
        ax = fig.add_subplot(1, 3, 2, projection=sdss_cutout.wcs)
        ax.imshow(sdss_cutout.data, cmap = 'gray_r', norm = norm, origin = 'lower')          
        ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')
        ax.set_title(sdss_rband_record.title)
    else:
        # We didn't find a suitable image, so leave that subplot blank.
        ax = fig.add_subplot(1, 3, 2, projection=galex_cutout.wcs)
        ax.set_title('SDSS rband image not found')
    
    # AllWISE
    
    # Find the AllWISE images that overlap the position.
    allwise_image_table = allwise_image_service.search(pos=pos, size=0)
    
    # Find the first AllWISE W1 channel image.
    allwise_image_record = None
    for record in allwise_image_table:
        if 'W1' in record.bandpass_id:
            allwise_image_record = record
            break
            
    if allwise_image_record is not None:
        # Create a cutout.
        file_name = download_file(allwise_image_record.getdataurl(), cache=True)  
        allwise_w1_image=fits.open(file_name)

        allwise_cutout = Cutout2D(allwise_w1_image[0].data, pos, (size, size),
                                  wcs=WCS(allwise_w1_image[0].header))

        # Plot the cutout in the third position of a 1x3 grid.
        ax = fig.add_subplot(1, 3, 3, projection=allwise_cutout.wcs)
        ax.imshow(allwise_cutout.data, cmap='gray_r', origin='lower', vmax = 10)
        ax.scatter(ra, dec, transform=ax.get_transform('fk5'), s=500, edgecolor='red', facecolor='none')
        ax.set_title(allwise_image_record.title)
    else:
        # We didn't find a suitable image, so leave that subplot blank.
        ax = fig.add_subplot(1, 3, 3, projection=galex_cutout.wcs)
        ax.set_title('AllWISE W1 image not found')
```
