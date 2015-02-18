#!/usr/bin/env python

"""
This script reads task data in iCalendar format and converts it to Gina
Trapani's todo.txt format (see http://todotxt.com/).

The task data can be exported from Remember The Milk or Apple's Reminders
app on OS X.
"""

USAGE = """
Convert iCalendar task data to a todo.txt file.
See README.md for details.

Usage:
    %s INPUT_ICS OUTPUT_TXT [APPENDIX]

Where:
    INPUT_ICS     : Pathname of the source iCalendar file.

    OUTPUT_TXT    : Pathname for the output todo.txt file.
                    The file must not exist.

    APPENDIX      : Text to append to each output line.

Examples:
    $ %s Reminders.ics todo.txt.Reminders +ListName

    $ %s iCalendar_Service.ics todo.txt.RTM
"""

import codecs
import re
import sys
import os

class ICSParser:
    """Quick and dirty iCalendar format parser."""

    def __init__(self, input_file):
        """Initialize a new parser object and parse the input file."""
        linebuf = None
        self.__node = {}
        self.__stack = []
        for line in input_file:
            line = line.rstrip('\r\n')
            if linebuf is None:
                linebuf = line
            else:
                if line[0] == ' ':
                    linebuf += line[1:]
                else:
                    self.__parse_line(linebuf)
                    linebuf = line
        if not linebuf is None:
            self.__parse_line(linebuf)

    def get_root(self):
        """Return the top-level VCALENDAR object."""
        return self.__node['VCALENDAR'][0]

    def __parse_line(self, line):
        """Parse an input line; update internal structures."""
        if line.startswith('BEGIN:'):
            self.__stack.append(self.__node)
            node_name = line[6:]
            new_node = {}
            if node_name in self.__node:
                self.__node[node_name].append(new_node)
            else:
                self.__node[node_name] = [new_node]
            self.__node = new_node
        elif line.startswith('END:'):
            self.__node = self.__stack.pop()
        else:
            key, val = tuple(line.split(':', 1))
            key = key.split(';', 1)[0]
            if not key in self.__node:
                self.__node[key] = val

def normalize_date(date):
    """Bring the date argument to a uniform format, which is YYYY-MM-DD."""
    # Remove the time portion.
    time_pos = date.find('T')
    if time_pos >= 0:
        date = date[:time_pos]
    # Insert dashes.
    if len(date) == 8:
        date = date[:4] + '-' + date[4:6] + '-' + date[6:]
    return date

def camel_case(words):
    """Convert a noun phrase to a CamelCase identifier."""
    result = ''
    for word in re.split('(?:\W|_)+', words):
        if word:
            if word[:1].islower():
                word = word.capitalize()
            result += word
    return result

def unescape(string):
    """Remove backslashes from the string."""
    return re.sub(r'\\(.)', r'\1', string)

def process_description(description):
    """Extract tags, location, and notes from the DESCRIPTION component."""
    result = ''
    sep = ' '
    next_sep = '; '
    for field in description.split(r'\n'):
        if field.startswith('Time estimate:') or \
                field.startswith('Updated:') or not field:
            continue
        elif field.startswith('Tags:'):
            tags = field[5:].strip()
            if tags != 'none':
                for tag in unescape(tags).split(','):
                    result += ' @' + camel_case(tag)
        elif field.startswith('Location:'):
            location = field[9:].strip()
            if location != 'none':
                result += ' @' + camel_case(location)
        elif re.match('^--+$', field):
            next_sep = ': '
        else:
            result += sep + unescape(field)
            sep = next_sep
            next_sep = '; '
    return result

def main(argv):
    """Convert input_file (iCalendar_Service.ics) to output_file (todo.txt)."""
    if len(argv) == 4:
        appendix = ' ' + argv[3]
    elif len(argv) == 3:
        appendix = ''
    else:
        print >> sys.stderr, USAGE % (argv[0], argv[0], argv[0])
        return 1
    input_file_name = argv[1]
    output_file_name = argv[2]
    if os.path.exists(output_file_name):
        print >> sys.stderr, "Error: '" + output_file_name + "' exists."
        return 1
    try:
        todos = ICSParser(codecs.open(input_file_name,
            'r', 'utf-8')).get_root()['VTODO']
        output_file = codecs.open(output_file_name, 'w', 'utf-8')
        for todo in todos:
            output_line = ''
            if 'STATUS' in todo and todo['STATUS'] == 'COMPLETED':
                output_line = 'x '
            if 'PRIORITY' in todo:
                output_line += '(' + \
                    chr(((ord(todo['PRIORITY']) - 49) >> 2) + 65) + ') '
            dates = set()
            for field in 'DTSTAMP', 'DTSTART', 'LAST-MODIFIED', 'COMPLETED':
                if field in todo:
                    dates.add(normalize_date(todo[field]))
            for date in sorted(dates, reverse=True):
                output_line += date + ' '
            output_line += unescape(todo['SUMMARY'])
            if 'URL' in todo:
                output_line += ' ' + todo['URL']
            if 'DUE' in todo:
                output_line += ' due:' + normalize_date(todo['DUE'])
            if 'DESCRIPTION' in todo:
                output_line += process_description(todo['DESCRIPTION'])
            print >> output_file, output_line + appendix
    except IOError, err:
        print >> sys.stderr, str(err)
        return 2
    print 'Conversion completed. Please carefully review the contents of'
    print output_file_name + ' before merging it into your existing todo.txt.'
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
