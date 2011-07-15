#!/usr/bin/env python

import xml.dom.minidom
import codecs
import sys

global of

class Task:
    def __init__(self):
        self.text = ''
        self.date = None
        self.url = None
        self.projects = None
        self.context = None

def ProcessSubDiv(subdiv):
    subdiv_class = subdiv.attributes['class'].nodeValue
    if subdiv_class.startswith('rtm_'):
        subdiv_class = subdiv_class[4:]
    if subdiv_class in ('due', 'time_estimate', 'postponed'):
        # Ignore these fields
        pass
    elif subdiv_class == 'notes':
        print >> of, subdiv_class
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
            print >> of, subdiv_class + ': ' + value
        elif subdiv_class == 'list':
            print >> of, subdiv_class + ': ' + value
        else:
            print >> of, subdiv_class + ': ' + value

def ProcessContent(content):
    if content.childNodes.length != 1:
        raise Exception, 'Invalid content length'

    div = content.firstChild
    if div.localName != 'div':
        raise Exception, 'Unknown content node ' + div.localName

    meta = ''

    for subdiv in div.childNodes:
        if subdiv.localName != 'div':
            raise Exception, 'Unknown div node ' + subdiv.localName

        field = ProcessSubDiv(subdiv)
        if field:
            if meta:
                meta = meta + ' ' + field
            else:
                meta = field

    return meta

try:
    dom = xml.dom.minidom.parse('Atom_Feed.xml')
    of = codecs.open('todo.txt.RTM', 'w', 'utf-8')

    for task in dom.getElementsByTagName('entry'):
        print >> of, '--------------------------------'
        updated = None
        title = ''
        meta = None
        for field in task.childNodes:
            if field.localName in ('author', 'link', 'id'):
                # Ignore these elements
                pass
            elif field.localName == 'updated':
                updated = field.firstChild.nodeValue
                time_pos = updated.find('T')
                if time_pos >= 0:
                    updated = updated[:time_pos]
            elif field.localName == 'title':
                title = field.firstChild.nodeValue
            elif field.localName == 'content':
                meta = ProcessContent(field)
            else:
                raise Exception, 'Unknown node ' + field.localName
        if updated:
            print >> of, updated,
        if meta:
            print >> of, title, meta
        else:
            print >> of, title
except Exception, e:
    print >> sys.stderr, e
