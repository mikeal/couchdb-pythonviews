#!/usr/bin/python
import os
for filename in ['genindex.html', 'index.html', 'modindex.html', 'search.html']:
    text = open(filename, 'r').read()
    f = open(filename, 'w')
    f.write(text.replace('_static', 'static'))
    f.close()