Description
===========

This repository contains two disposable scripts that can convert iCalendar
or Remember The Milk tasks to Gina Trapani's todo.txt format (see
https://github.com/todotxt):

- ``ics_to_todotxt.py`` can import VTODO entries from iCalendar (.ics) files,
  including those created by RTM;
- ``rtm_atom_to_todotxt.py`` can import tasks from your RTM Atom feed.

Run each script without arguments for the usage information.

Import tasks from Remember The Milk
===================================

Remember The Milk can export data in iCalendar format, and
``ics_to_todotxt.py`` is the preferred method of importing from RTM.

RTM lists are converted to todo.txt projects (``+Project``); RTM tags and
locations are converted to contexts (``@Context``). Unfortunately, although
iCalendar format contains much more information about tasks, it's missing
the RTM list names, so if those are important, there are two options:

1. Use ``rtm_atom_to_todotxt.py``.
2. Reconstruct the list names in the ``ics_to_todotxt.py`` output manually.

To use ``ics_to_todotxt.py``, RTM task data in iCalendar format must be
downloaded and saved using a web browser from this URL:

    https://www.rememberthemilk.com/icalendar/YOUR_RTM_USERNAME/

To download RTM task data as an Atom feed for ``rtm_atom_to_todotxt.py``,
the following URL must be used instead:

    https://www.rememberthemilk.com/atom/YOUR_RTM_USERNAME/

The last component in both URLs must be replaced with the actual RTM
username.  The user must be logged in.
