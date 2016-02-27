NYC Turnstyle Data
==================

By Jonah Joselow


Data/
-----
Put data in the `data/` directory

August 1 Analysis
-----------------
Accomplished in a ipython notebook. Please read thru. Put comments throughout

MTAReader
---------
Class which implements the logic implicitly formed above. Wanted to make the
notebooks smaller and get code reuse for the future pieces. I think it is best
to first explore the data a bit before I decide on a given format, so I did this
second.


July Analysis
-------------
Accomplished in a ipython notebook. Please read thru. Put comments throughout

Insert Into DB
--------------
Prepares and inserts into the DB, after the django project has been initialized.
I do some simple post processing to remove errors in the MTA data

mta-django
----------

Django app. out some screenshots in `mta-django-screenshots`

Features:

- Perform analysis on 3 stats: `Entries`, `Exits`, `Busyness`
- Select dates by day, range, or custom
- Split on either `Stations`, `SCP` (turnstiles), or Both
- Finally, bin the data by day, hour, or minute

Grids:

- One per raw, min, max, and mean.
- draw columns, resize, filter and sort using [ag-grid](https://www.ag-grid.com).

This library is great, because it works on all web platforms, native JS, Angular,
React, etc. Plus I have it scaling at work well beyond 200,000 rows (which
constantly update). Performance of the DOM would crash the site by then, so this
library only draws roughly the rows you immediely see. I am using on ITG Prism 2,
our realtime Algo monitoring app.
