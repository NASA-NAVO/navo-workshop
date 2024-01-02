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
  version: 3.6.10
nav_menu: {}
toc:
  navigate_menu: true
  number_sections: true
  sideBar: true
  threshold: 6
  toc_cell: false
  toc_section_display: block
  toc_window_display: true
---

# Spectral Access

This notebook is one of a set produced by NAVO to demonstrate data access with python tools.

In this notebook, we show how to search for and retrieve spectra from VO services using the Registry and the __[Simple Spectral Access](http://www.ivoa.net/documents/SSA/)__ (SSA) protocol.

```{code-cell} ipython3
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
%matplotlib inline

import requests, io

from astropy.table import Table
import astropy.io.fits as fits
from astropy.coordinates import SkyCoord
# For downloading files
from astropy.utils.data import download_file

import pyvo as vo

# There are a number of relatively unimportant warnings that show up, so for now, suppress them:
import warnings
warnings.filterwarnings("ignore", module="astropy.io.votable.*")
warnings.filterwarnings("ignore", module="pyvo.utils.xml.*")
```

## Finding available Spectral Access Services

First, we find out what spectral access services ('ssa') are available in the Registry offering x-ray data.

```{code-cell} ipython3
services = vo.regsearch(servicetype='ssa',waveband='x-ray')
services.to_table()['ivoid','short_name']
```

We can look at only the Chandra entry:

```{code-cell} ipython3
chandra_service = [s for s in services if 'Chandra' in s.short_name][0]
chandra_service.access_url
```

## Chandra Spectrum of Delta Ori

Getting the list of spectra.

```{code-cell} ipython3
delori = SkyCoord.from_name("Delta Ori")

spec_tables = chandra_service.search(pos=delori,diameter=0.1)
spec_tables.to_table().show_in_notebook()
```

Accessing one of the spectra.

```{code-cell} ipython3
## If you only run this once, you can do it in memory in one line:
##  This fetches the FITS as an astropy.io.fits object in memory
# hdu_list = spec_tables[0].getdataobj()
## But if you might run this notebook repeatedly with limited bandwidth,
##  download it once and cache it.
file_name = download_file(spec_tables[0].getdataurl(),cache=True)
hdu_list = fits.open(file_name)
```

## Simple example of plotting a spectrum

```{code-cell} ipython3
spec_table = Table(hdu_list[1].data)
spec_table
```

```{code-cell} ipython3
matplotlib.rcParams['figure.figsize'] = (12, 10)

for i in range(len(spec_table)):

    ax = plt.subplot(6,2,i+1)
    pha = plt.plot( spec_table['CHANNEL'][i],spec_table['COUNTS'][i])
    ax.set_yscale('log')

    if spec_table['TG_PART'][i] == 1:
        instr='HEG'
    if spec_table['TG_PART'][i] == 2:
        instr='MEG'
    if spec_table['TG_PART'][i] == 3:
        instr='LEG'

    ax.set_title("{grating}{order:+d}".format(grating=instr, order=spec_table['TG_M'][i]))

    plt.tight_layout()
```

This can then be analyzed in your favorite spectral analysis tool, e.g., [pyXspec](https://heasarc.gsfc.nasa.gov/xanadu/xspec/python/html/index.html).  (For the winter 2018 AAS workshop, we demonstrated this in a [notebook](https://github.com/NASA-NAVO/aas_workshop_2018/blob/master/heasarc/heasarc_Spectral_Access.md) that you can consult for how to use pyXspec, but the pyXspec documentation will have more information.)

```{code-cell} ipython3

```
