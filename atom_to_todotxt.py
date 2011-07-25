#!/usr/bin/env python

import xml.dom.minidom
import codecs
import sys
import re

class Task:
    def __init__(self):
        self.__priority = ''
        self.__date = ''
        self.__descr = ''
        self.__url = ''
        self.__notes = ''
        self.__project = ''
        self.__contexts = set()

    def parse_entry(self, entry):
        for field in entry.childNodes:
            if field.localName in ('author', 'link', 'id'):
                # Ignore these elements
                pass
            elif field.localName == 'updated':
                self.__date = field.firstChild.nodeValue
                time_pos = self.__date.find('T')
                if time_pos >= 0:
                    self.__date = self.__date[:time_pos]
                self.__date += ' '
            elif field.localName == 'title':
                self.__descr = field.firstChild.nodeValue
            elif field.localName == 'content':
                self.__process_content(field)
            else:
                raise Exception, 'Unknown node ' + field.localName

    def convert(self):
        result = self.__priority + self.__date + self.__descr + \
            self.__url + self.__notes + self.__project
        if self.__contexts:
            result += ' @' + ' @'.join(self.__contexts)
        return result

    def __process_subdiv(self, subdiv):
        subdiv_class = subdiv.attributes['class'].nodeValue
        if subdiv_class.startswith('rtm_'):
            subdiv_class = subdiv_class[4:]
        if subdiv_class in ('due', 'time_estimate', 'postponed'):
            # Ignore these fields
            pass
        elif subdiv_class == 'notes':
            for note_div in subdiv.childNodes:
                note_class = note_div.attributes['class'].nodeValue
                if note_class != 'rtm_note':
                    raise Exception, 'Invalid note class: ' + note_class
                if note_div.childNodes.length != 3:
                    raise Exception, 'Unexpected number of children in a note'
                (note_title, note_content) = note_div.childNodes[:2]
                self.__notes += ' ' + \
                    note_title.firstChild.firstChild.nodeValue + ': ' + \
                    repr(note_content.firstChild.nodeValue)
        else:
            if subdiv.childNodes.length != 2:
                raise Exception, 'Invalid subdiv node size (' + \
                    str(subdiv.childNodes.length) + '); class: ' + subdiv_class

            value = subdiv.lastChild.firstChild
            if subdiv_class == 'url':
                value = value.firstChild
            value = value.nodeValue

            if value != 'none':
                if subdiv_class == 'priority':
                    self.__priority = '(' + chr(ord(value) + 16) + ') '
                elif subdiv_class == 'url':
                    self.__url = ' URL: ' + value
                elif subdiv_class == 'list':
                    self.__project = ' +' + self.__capitalize(value)
                elif subdiv_class == 'location':
                    self.__contexts.add(self.__capitalize(value))
                elif subdiv_class == 'tags':
                    for tag in value.split(', '):
                        self.__contexts.add(self.__capitalize(tag))
                else:
                    raise Exception, 'Invalid subdiv class: ' + subdiv_class

    def __process_content(self, content):
        if content.childNodes.length != 1:
            raise Exception, 'Invalid content length'

        content = content.firstChild
        if content.localName != 'div':
            raise Exception, 'Unexpected content node ' + content.localName

        for subdiv in content.childNodes:
            if subdiv.localName != 'div':
                raise Exception, 'Unknown div node ' + subdiv.localName
            self.__process_subdiv(subdiv)

    @staticmethod
    def __capitalize(words):
        result = ''
        for word in re.split('(?:\W|_)+', words):
            if word:
                if word[:1].islower():
                    word = word.capitalize()
                result += word
        return result

try:
    dom = xml.dom.minidom.parse('Atom_Feed.xml')
    output_file_name = 'todo.txt.RTM'
    output_file = codecs.open(output_file_name, 'w', 'utf-8')

    for entry in dom.getElementsByTagName('entry'):
        task = Task()
        task.parse_entry(entry)
        print >> output_file, task.convert()

    print 'Conversion completed. Please carefully review the contents of'
    print output_file_name + ' before merging it into your todo.txt.'

except Exception, e:
    print >> sys.stderr, e
