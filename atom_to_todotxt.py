#!/usr/bin/env python

import xml.dom.minidom
import codecs
import sys

global output_file

class Task:
    def __init__(self):
        self.text = ''
        self.date = None
        self.url = None
        self.projects = None
        self.context = None

        self.updated = None
        self.title = ''
        self.meta = None

    def parse_entry(self, entry):
        for field in entry.childNodes:
            if field.localName in ('author', 'link', 'id'):
                # Ignore these elements
                pass
            elif field.localName == 'updated':
                task.updated = field.firstChild.nodeValue
                time_pos = task.updated.find('T')
                if time_pos >= 0:
                    task.updated = task.updated[:time_pos]
            elif field.localName == 'title':
                task.title = field.firstChild.nodeValue
            elif field.localName == 'content':
                task.meta = self.process_content(field)
            else:
                raise Exception, 'Unknown node ' + field.localName

    def output(self, output_file):
        if self.updated:
            print >> output_file, self.updated,
        if self.meta:
            print >> output_file, self.title, self.meta
        else:
            print >> output_file, self.title

    def process_subdiv(self, subdiv):
        subdiv_class = subdiv.attributes['class'].nodeValue
        if subdiv_class.startswith('rtm_'):
            subdiv_class = subdiv_class[4:]
        if subdiv_class in ('due', 'time_estimate', 'postponed'):
            # Ignore these fields
            pass
        elif subdiv_class == 'notes':
            print >> output_file, subdiv_class
        else:
            if subdiv.childNodes.length != 2:
                raise Exception, 'Invalid subdiv node size (' + \
                    str(subdiv.childNodes.length) + '); class: ' + subdiv_class

            value = subdiv.lastChild.firstChild
            if subdiv_class == 'url':
                value = value.firstChild
            value = value.nodeValue

            #if value != 'none':
            if subdiv_class == 'url':
                print >> output_file, subdiv_class + ': ' + value
            elif subdiv_class == 'list':
                print >> output_file, subdiv_class + ': ' + value
            else:
                print >> output_file, subdiv_class + ': ' + value

    def process_content(self, content):
        if content.childNodes.length != 1:
            raise Exception, 'Invalid content length'

        div = content.firstChild
        if div.localName != 'div':
            raise Exception, 'Unknown content node ' + div.localName

        meta = ''

        for subdiv in div.childNodes:
            if subdiv.localName != 'div':
                raise Exception, 'Unknown div node ' + subdiv.localName

            field = self.process_subdiv(subdiv)
            if field:
                if meta:
                    meta = meta + ' ' + field
                else:
                    meta = field

        return meta

try:
    dom = xml.dom.minidom.parse('Atom_Feed.xml')
    output_file = codecs.open('todo.txt.RTM', 'w', 'utf-8')

    for entry in dom.getElementsByTagName('entry'):
        print >> output_file, '--------------------------------'
        task = Task()
        task.parse_entry(entry)
        task.output(output_file)
except Exception, e:
    print >> sys.stderr, e
