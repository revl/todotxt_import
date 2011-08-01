#!/usr/bin/env python

import codecs
import sys
import re

class ICSParser:
    def parse_file(self, input_file):
        self.linebuf = None
        self.node = {}
        self.stack = []
        for line in input_file:
            line = line.rstrip('\n')
            if self.linebuf is None:
                self.linebuf = line
            else:
                if line[0] == ' ':
                    self.linebuf += line[1:]
                else:
                    self.__parse_line(self.linebuf)
                    self.linebuf = line
        if not self.linebuf is None:
            self.__parse_line(self.linebuf)
        return self.node

    def __parse_line(self, line):
        if line.startswith('BEGIN:'):
            self.stack.append(self.node)
            node_name = line[6:]
            new_node = {}
            if node_name in self.node:
                self.node[node_name].append(new_node)
            else:
                self.node[node_name] = [new_node]
            self.node = new_node
        elif line.startswith('END:'):
            self.node = self.stack.pop()
        else:
            key, val = tuple(line.split(':', 1))
            key = key.split(';', 1)[0]
            if not key in self.node:
                self.node[key] = val

class Task:
    def __init__(self):
        self.__priority = ''
        self.__dates = set()
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

try:
    input_file = codecs.open('iCalendar_Service.ics', 'r', 'utf-8')
    tasks = ICSParser().parse_file(input_file)['VCALENDAR'][0]['VTODO']
    output_file_name = 'todo.txt.RTM'
    output_file = codecs.open(output_file_name, 'w', 'utf-8')

    for task in tasks:
        print >> output_file, repr(task)

    print 'Conversion completed. Please carefully review the contents of'
    print output_file_name + ' before merging it into your todo.txt.'

except Exception, e:
    print >> sys.stderr, e
