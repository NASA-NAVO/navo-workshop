---
jupytext:
  notebook_metadata_filter: all
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.2
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
  version: 3.11.9
---

# UCDs (Unified Content Descriptors)

Suppose you want to do something using a column that you expect to find in a bunch of different tables, like coordinates and time.  It's a good bet that many if not most of the tables have coordinate columns, but there's no rule about what they have to be named.

When doing detailed catalog queries with the TAP, you can obviously examine the columns of every table you're interested in to find the columns you want.  Then you can hard-code the correct ones into each query for each table and service.

Or, you can also search for keywords like "ra" or "ascension" in the columns and their descriptions to get the columns you want automatically that way.

But is there are more generic way?  [Unified Content Descriptors (UCDs)](http://www.ivoa.net/documents/latest/UCD.html) are a VO standard that allows table publishers to name their columns whatever they (or their contributors) want but to identify those that contain standard sorts of data.  For example, the RA column could be called "RA", "ra", "Right_Ascension", etc.  But in all cases, a VO service can label the column with its UCD, which is "pos.eq.ra".  This information is not part of the table but part of the meta-data that the service may provide with that data. Though not required of all VO services, UCDs are commonly provided precisely to make such tasks as identifying the columns of interest easier to automate.

This is easiest to show by example.

```{code-cell} ipython3
# Generic VO access routines
import pyvo as vo

# Ignore unimportant warnings
import warnings
warnings.filterwarnings('ignore', '.*Unknown element .*', vo.utils.xml.elements.UnknownElementWarning)
```

Let's look at some tables in a little more detail.  Let's find the Hubble Source Catalog version 3 (HSCv3), assuming there's only one at MAST.

```{code-cell} ipython3
services = vo.regsearch(servicetype='tap', keywords=['mast'])
hsc=[s for s in services if 'HSCv3' in s.res_title][0]

print(f'Title: {hsc.res_title}')
print(f'{hsc.res_description}')
```

Now let's see what tables are provided by this service for HSCv3.  Note that this is another query to the service:

```{code-cell} ipython3
tables = hsc.service.tables  # Queries for details of the service's tables
print(f'{len(tables)} tables:')
for t in tables:
    print(f'{t.name:30s} - {t.description}\n----')  # A more succinct option than t.describe()
```

Let's look at the first 10 columns of the DetailedCatalog table.  Again, note that calling the columns attribute sends another query to the service to ask for the columns.

```{code-cell} ipython3
columns=tables['dbo.detailedcatalog'].columns
for c in columns:
    print(f'{f"{c.name} [{c.ucd}]":30s} - {c.description}')
```

The PyVO method to get the columns will automatically fetch all the meta-data about those columns.  It's up to the service provider to set them correctly, of course, but in this case, we see that the column named "matchra" is identified with the UCD "pos.eq.ra".

So if we did not know the exact name used in HSCv3 for the RA, we could do something like this looking for the string "ra":

```{code-cell} ipython3
ra_name=[c.name for c in columns if 'ra' in c.name.lower() or "ascension" in c.name.lower()]
print(ra_name)
```

Since that guessing doesn't give a unique answer, the more general and reliable approach is to check for the correct UCD.  It also has the further advantage that it can be used to label columns that should be used for certain purposes when there are multiple possibilities.  For instance, this table has MatchRA and SourceRA.  Let's check the UCD:

(Note that the UCD is not required.  If it isn't there, you get a None type, so code the check carefully)

```{code-cell} ipython3
ra_name=[c.name for c in columns if c.ucd and 'pos.eq.ra' in c.ucd][0]
dec_name=[c.name for c in columns if c.ucd and 'pos.eq.dec' in c.ucd][0]
ra_name,dec_name
```

What that shows you is that though there are two columns in this table that give RA information, only one has the 'pos.eq.ra' UCD. The documentation for this ought to explain the usage of these columns, and the UCD should not be used as a substitute for understanding the table. But it can be a useful tool.

+++

In particular, you can use the UCDs to look for catalogs that might have the information you're interested in. Then you can code the same query to work for different tables (with different column names) in a loop.  This sends a bunch of queries but doesn't take too long, a minute maybe. (One is particularly slow.)

```{code-cell} ipython3
#  Look for all TAP services with x-ray and optical data
collection={}
for s in vo.regsearch(servicetype='tap',keywords=['x-ray','optical']):
    if "wfau" in s.ivoid:  continue #  These sometimes have issues
    print(f"Looking at service from {s.ivoid}")
    try:
        tables=s.service.tables
    except:
        print("Problem with this service's tables endpoint.  Continuing to next.")
        continue
    #  Find all the tables that have an RA,DEC and a start and end time
    for t in tables:
        names={}
        for ucd in ['pos.eq.ra','pos.eq.dec','time.start','time.end']:
            cols=[c.name for c in t.columns if c.ucd and ucd in c.ucd]
            if len(cols) > 0:
                names[ucd]=cols[0]  # use the first that matches
        if len(names.keys()) == 4:
            print(f"    Table {t.name} has the right columns.  Counting rows matching my time.")
            #  For a first look, a very simple query counting rows in a
            #  time range of interest:
            query=f"select count({names['time.start']}) from {t.name}" \
                  f" where {names['time.start']} > 52000 "
            try:
                results=s.search(query)
            except:
                print("Problem executing query.  Continuing to next.")
                continue
            #  For this simple query, the result is a single number, the count.
            #   But different services might name the result differently, so
            #   don't assume you know the column  name.
            print("    Found {} results from {}\n".format(results.to_table()[0][0],t.name))
            #  If the query above asked for the matching data rather than the
            #  count, you might want to collect the results.
            #  Careful:  here we're assuming the table names are unique
            collection[t.name]=results
```

You can also use UCDs to look at the results.  Above, we collected just the first 10 rows of the four columns we're interested in from every catalog that had them.  But these tables still have their original column names.  So the UCDs will still be useful, and PyVO provides a simple routine to convert from UCD to column (field) name.

Note, however,  that returning the UCDs as part of the result is not mandatory, and some services do not do it.  So you'll have to check.

Now we have a collection of rows from different tables with different columns.  In the results object, we have access to a fieldname_with_ucd() function to get the column you want.  Supposing we hadn't already looked for this in the above loop, let's now find out which of these tables has a magnitude column:

```{code-cell} ipython3
#ucd='pos.eq.ra'
ucd='phot.mag'
for tname,results in collection.items():
    #print(f"On table {tname}")
    #  Sometimes this doesn't work well, so use a try:
    try:
        name=results.fieldname_with_ucd(ucd)
    except:
        pass
    if name:
        print(f"  Table {tname} has the {ucd} column named {name}")
    else:
        print(f"  (Table {tname} didn't find the UCD.)")
```

Lastly, if you have a table of results from a TAP query (and if that service includes the UCDs), then you can get data based on UCDs with the getbyucd() method, which simply gets the corresponding element using fieldname_with_ucd():

```{code-cell} ipython3
results=hsc.service.search("select top 10 * from dbo.detailedcatalog")
[r.getbyucd('phot.mag') for r in results]
```

Note that we can see earlier in this notebook, when we looked at this table's contents, that there are two phot.mag fields in this table, MagAper2 and MagAuto.  The getbyucd() and fieldname_with_ucd() routines do not currently allow you to handle multiple columns with the same UCD.  The code can help you find what you want, but it depends on the meta data the service defines, and you still must look at the detailed information for each catalog you use to understand what it contains.

```{code-cell} ipython3

```
