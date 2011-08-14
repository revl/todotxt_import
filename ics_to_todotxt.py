#!/usr/bin/env python

import codecs
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

def convert_date(date):
    time_pos = date.find('T')
    if time_pos >= 0:
        date = date[:time_pos]
    if len(date) == 8:
        date = date[:4] + '-' + date[4:6] + '-' + date[6:]
    return date

def capitalize(words):
    result = ''
    for word in re.split('(?:\W|_)+', words):
        if word:
            if word[:1].islower():
                word = word.capitalize()
            result += word
    return result

def unescape(string):
    return re.sub(r'\\(.)', r'\1', string)

input_file = codecs.open('iCalendar_Service.ics', 'r', 'utf-8')
todos = ICSParser().parse_file(input_file)['VCALENDAR'][0]['VTODO']
output_file_name = 'todo.txt.RTM'
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
            dates.add(convert_date(todo[field]))
    for date in sorted(dates, reverse=True):
        output_line += date + ' '
    output_line += unescape(todo['SUMMARY'])
    if 'URL' in todo:
        output_line += ' ' + todo['URL']
    if 'DUE' in todo:
        output_line += ' due:' + convert_date(todo['DUE'])
    sep = ' '
    next_sep = '; '
    for field in todo['DESCRIPTION'].split(r'\n'):
        if field.startswith('Time estimate:') or \
                field.startswith('Updated:') or not field:
            continue
        elif field.startswith('Tags:'):
            tags = field[5:].strip()
            if tags != 'none':
                for tag in unescape(tags).split(','):
                    output_line += ' @' + capitalize(tag)
        elif field.startswith('Location:'):
            location = field[9:].strip()
            if location != 'none':
                output_line += ' @' + capitalize(location)
        elif re.match('^--+$', field):
            next_sep = ': '
        else:
            output_line += sep + unescape(field)
            sep = next_sep
            next_sep = '; '
    print >> output_file, output_line

print 'Conversion completed. Please carefully review the contents of'
print output_file_name + ' before merging it into your todo.txt.'
