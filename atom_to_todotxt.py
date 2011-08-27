#!/usr/bin/env python

"""
This script reads Remember The Milk task data as an Atom feed, which can
be downloaded from https://www.rememberthemilk.com/atom/YOUR_RTM_USER_NAME/
and converts it to Gina Trapani's todo.txt format (see http://todotxt.com/).

The script looks for an input file named 'Atom_Feed.xml' in the current
directory and saves its output as 'todo.txt.RTM'.
"""

import xml.dom.minidom
import codecs
import re
import sys

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
            raise ConversionError, 'Invalid content length'
        content = content.firstChild
        if content.localName != 'div':
            raise ConversionError, 'Unexpected content node ' + str(content)
        for subdiv in content.childNodes:
            if subdiv.localName != 'div':
                raise ConversionError, 'Unknown div node ' + subdiv.localName
            subdiv_class = subdiv.attributes['class'].nodeValue
            if subdiv_class == 'rtm_notes':
                self.__process_notes(subdiv)
            else:
                self.__process_subdiv(subdiv, subdiv_class)

    def __process_subdiv(self, subdiv, subdiv_class):
        """Extract task attributes: URL, list, tags, location, etc."""
        if subdiv.childNodes.length != 2:
            raise ConversionError, 'Invalid subdiv node size (' + \
                str(subdiv.childNodes.length) + '); class: ' + subdiv_class
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
                raise ConversionError, 'Invalid note class: ' + note_class
            if note_div.childNodes.length != 3:
                raise ConversionError, 'Unexpected number of children in a note'
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

def main():
    """Convert input_file (Atom_Feed.xml) to output_file (todo.txt)."""
    input_file_name = 'Atom_Feed.xml'
    try:
        dom = xml.dom.minidom.parse(input_file_name)
    except Exception, err:
        print >> sys.stderr, input_file_name + ': ' + str(err)
        return 1
    remove_whitespace(dom)
    output_file_name = 'todo.txt.RTM'
    try:
        output_file = codecs.open(output_file_name, 'w', 'utf-8')
        for entry in dom.getElementsByTagName('entry'):
            print >> output_file, TaskConverter(entry).convert()
    except IOError, err:
        print >> sys.stderr, output_file_name + ': ' + str(err)
        return 2
    except ConversionError, err:
        print >> sys.stderr, str(err)
        return 3
    print 'Conversion completed. Please carefully review the contents of'
    print output_file_name + ' before merging it into your todo.txt.'
    return 0

if __name__ == "__main__":
    sys.exit(main())
