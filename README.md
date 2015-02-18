Description
===========

This repository contains two disposable Python scripts that take a list
of tasks exported from Remember The Milk or the Reminders app for OS X and
convert that list to Gina Trapani's todo.txt format (see http://todotxt.com/).

Usage
=====

There are two scripts in the package: ``ics_to_todotxt.py``, which can
be used with both Remember The Milk and Apple's Reminders app, and
``rtm_atom_to_todotxt.py``, which can only be used with Remember The Milk.

Run each script without arguments for the usage information.

Import tasks from OS X Reminders app or iCal 5.X
------------------------------------------------

To import tasks from OS X Reminders:

1. Open the Reminders app.
2. In the left pane, select the list(s) you want to export.
3. From the menu bar, select "File" > "Export...", choose
   where to save the ICS file, click "Export".

To import tasks from iCal:

1. Open iCal.
2. Make sure Reminders are visible: "View" > "Show Reminders".
3. While holding the Control key, click the name of the
   reminder list to be exported and then choose "Export...".
4. Choose a location for the ICS file, and then click "Export".

When importing ICS files prepared by Reminders or iCal, the names of
the lists are lost, so if this information is important, one must import
tasks on per-list basis and add ``+Project`` names manually, for example,
by providing the third argument to ``ics_to_todotxt.py``.

Import tasks from Remember The Milk
-----------------------------------

In addition to ``ics_to_todotxt.py``, which expects data in iCalendar
format, RTM tasks can also be imported using ``rtm_atom_to_todotxt.py``,
which requires an Atom feed downloaded from rememberthemilk.com.
The former script is the preferred method though.

RTM lists are coverted to todo.txt projects (``+Project``); RTM tags and
locations are converted to contexts (``@Context``). Unfortunately, although
iCalendar format contains much more information about tasks, it's missing
the RTM list names, so if those are important, there are two options:

1. Use ``rtm_atom_to_todotxt.py``.
2. Reconstruct the list names in ``ics_to_todotxt.py`` output manually.

RTM task data in iCalendar format to be used by ``ics_to_todotxt.py``
must be downloaded and saved using a web browser from this URL:

    https://www.rememberthemilk.com/icalendar/YOUR_RTM_USER_NAME/

To download RTM task data as an Atom feed for the ``rtm_atom_to_todotxt.py``
script, the following URL must be used instead:

    https://www.rememberthemilk.com/atom/YOUR_RTM_USER_NAME/

The last component in both URLs must be replaced with the actual RTM user
name.  The user must be logged in.
