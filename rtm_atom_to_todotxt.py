#!/usr/bin/env python3

"""
This script converts Remember The Milk task data in the form of an
Atom feed to Gina Trapani's todo.txt format (see http://todotxt.com/).
"""

USAGE = """
Convert Remember The Milk task list to a todo.txt file.

This script takes an Atom feed downloaded from the Remember The Milk
website as its input. The feed must be downloaded using a web browser
from this URL:

https://www.rememberthemilk.com/atom/YOUR_RTM_USER_NAME/

The last URL component must be replaced with actual RTM user name.
The user must be logged in.

Usage:
    {0} INPUT_XML OUTPUT_TXT

Where:
    INPUT_XML     : Pathname of the source Atom feed.

    OUTPUT_TXT    : Pathname for the output todo.txt file.
                    The file must not exist.

Example:
    {0} Atom_Feed.xml todo.txt.RTM
"""

import xml.dom.minidom
import codecs
import re
import sys
import os.path

class ConversionError(Exception):
    """Exception raised for unexpected input XML structure."""
    pass

class TaskConverter:
    """Helper class for converting RTM tasks in Atom format to todo.txt."""

    def __init__(self, entry):
        """Parse the <entry> element; save parsing results in 'self'."""
        self.__priority = ''
        self.__date = ''
        self.__descr = ''
        self.__url = ''
        self.__notes = ''
        self.__project = ''
        self.__contexts = set()
        for field in entry.childNodes:
            if field.localName == 'updated':
                self.__date = field.firstChild.nodeValue
                time_pos = self.__date.find('T')
                if time_pos >= 0:
                    self.__date = self.__date[:time_pos]
                self.__date += ' '
            elif field.localName == 'title':
                self.__descr = field.firstChild.nodeValue
            elif field.localName == 'content':
                self.__process_content(field)

    def convert(self):
        """Return the results of parsing as a line in todo.txt format."""
        todo = self.__priority + self.__date + self.__descr + \
            self.__url + self.__notes + self.__project
        if self.__contexts:
            todo += ' @' + ' @'.join(self.__contexts)
        return todo

    def __process_content(self, content):
        """Process the <content> part of <entry>."""
        if content.childNodes.length != 1:
            raise ConversionError('Invalid content length')
        content = content.firstChild
        if content.localName != 'div':
            raise ConversionError('Unexpected content node {}'.format(content))
        for subdiv in content.childNodes:
            if subdiv.localName != 'div':
                raise ConversionError(
                    'Unknown div node {}'.format(subdiv.localName))
            subdiv_class = subdiv.attributes['class'].nodeValue
            if subdiv_class == 'rtm_notes':
                self.__process_notes(subdiv)
            else:
                self.__process_subdiv(subdiv, subdiv_class)

    def __process_subdiv(self, subdiv, subdiv_class):
        """Extract task attributes: URL, list, tags, location, etc."""
        if subdiv.childNodes.length != 2:
            raise ConversionError(
                'Invalid subdiv node size ({}); class: {}'.format(
                    subdiv.childNodes.length, subdiv_class))
        value = subdiv.lastChild.firstChild
        if subdiv_class == 'rtm_url':
            value = value.firstChild
        value = value.nodeValue
        if value != 'none':
            if subdiv_class == 'rtm_priority':
                self.__priority = '(' + chr(ord(value) + 16) + ') '
            elif subdiv_class == 'rtm_url':
                self.__url = ' ' + value
            elif subdiv_class == 'rtm_list':
                self.__project = ' +' + self.__camel_case(value)
            elif subdiv_class == 'rtm_location':
                self.__contexts.add(self.__camel_case(value))
            elif subdiv_class == 'rtm_tags':
                for tag in value.split(','):
                    self.__contexts.add(self.__camel_case(tag))

    def __process_notes(self, notes_subdiv):
        """Handle task notes, a special case of task attributes."""
        for note_div in notes_subdiv.childNodes:
            note_class = note_div.attributes['class'].nodeValue
            if note_class != 'rtm_note':
                raise ConversionError(
                    'Invalid note class: {}'.format(note_class))
            if note_div.childNodes.length != 3:
                raise ConversionError('Unexpected number of children in a note')
            (note_title, note_content) = note_div.childNodes[:2]
            self.__notes += ' ' + \
                note_title.firstChild.firstChild.nodeValue + ': ' + \
                repr(note_content.firstChild.nodeValue)

    @staticmethod
    def __camel_case(phrase):
        """Convert a noun phrase to a CamelCase identifier."""
        result = ''
        for word in re.split('(?:\W|_)+', phrase):
            if word:
                if word[:1].islower():
                    word = word.capitalize()
                result += word
        return result

def remove_whitespace(parent_dom_node):
    """Remove all whitespace-only DOM nodes."""
    blank_nodes = []
    for node in parent_dom_node.childNodes:
        if node.nodeType == xml.dom.Node.TEXT_NODE and not node.data.strip():
            blank_nodes.append(node)
        elif node.hasChildNodes():
            remove_whitespace(node)
    for node in blank_nodes:
        parent_dom_node.removeChild(node)
        node.unlink()

def main(argv):
    """Convert input_file (Atom_Feed.xml) to output_file (todo.txt)."""
    if len(argv) != 3:
        print(USAGE.format(argv[0]), file=sys.stderr)
        return 1
    (input_file_name, output_file_name) = argv[1:]
    if os.path.exists(output_file_name):
        print("Error: '{}' exists.".format(output_file_name), file=sys.stderr)
        return 1
    try:
        dom = xml.dom.minidom.parse(input_file_name)
    except IOError as err:
        print(err, file=sys.stderr)
        return 2
    except Exception as err:
        print('{}: {}'.format(input_file_name, err), file=sys.stderr)
        return 2
    remove_whitespace(dom)
    try:
        output_file = codecs.open(output_file_name, 'w', 'utf-8')
        for entry in dom.getElementsByTagName('entry'):
            print(TaskConverter(entry).convert(), file=output_file)
    except IOError as err:
        print(err, file=sys.stderr)
        return 3
    except ConversionError as err:
        print(err, file=sys.stderr)
        return 3
    print('Conversion completed. Please carefully review the contents of')
    print(output_file_name + ' before merging it into your existing todo.txt.')
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
