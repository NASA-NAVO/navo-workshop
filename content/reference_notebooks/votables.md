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
  version: 3.9.1
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
---

# VO Tables

## Create a VO Table from an Astropy Table

+++

There are several ways of doing this, and there are a few object layers here, which can be confusing:

- Standard [astropy Table](https://docs.astropy.org/en/stable/table/) objects
- [Votable Table](https://docs.astropy.org/en/stable/api/astropy.io.votable.tree.Table.html#astropy.io.votable.tree.Table) objects
- [Votable VOTableFile](https://docs.astropy.org/en/stable/api/astropy.io.votable.tree.VOTableFile.html#astropy.io.votable.tree.VOTableFile) objects (may contain multiple votable Tables)

Although some things can be done with generic astropy Tables, other VO operations can only be done with VO Tables or VOTableFile objects.

This is easiest to see with an example.

```{code-cell} ipython3
import io, numpy

from astropy import table as aptable
from astropy.io import votable as apvot
```

## Create a table with only two columns starting from an astropy Table

```{code-cell} ipython3
myaptable=aptable.Table(
    numpy.array([
            [19.0186,       46.7304],
            [20.2887,       40.4703],
            [125.886,       21.3377],
            [136.002,       21.9679],
            [141.057,       40.6372],
            [146.700,       22.0116],
            [148.785,       14.2922],
            [149.751,       17.8168],
            [175.039,       15.3270],
            [191.542,       30.7317],
            [194.913,       28.8959],
            [199.026,       41.5011],
            [206.577,       43.8511],
            [209.963,       38.1821],
            [213.556,       15.6214],
            [219.967,       42.7421],
            [226.693,       12.8502],
            [237.489,       20.8057],
            [241.519,       20.8014],
            [317.088,       18.2002],
            [329.235,       6.64845],
            [333.830,       37.3012] ]),
    names=["RA","DEC"])

print(type(myaptable))
print(myaptable)
```

## Then convert this to a VOTableFile object which contains a nested set of *resources* and *tables* (in this case, only one of each)

```{code-cell} ipython3
myvotablefile = apvot.from_table(myaptable)
print(type(myvotablefile))

for r in myvotablefile.resources:
    mytable=r
    for t in r.tables:
        print(t)
```

```{code-cell} ipython3

```
