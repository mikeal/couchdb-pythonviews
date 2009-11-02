import os
import copy
from datetime import datetime
from couchquery import Database, createdb, deletedb

this_directory = os.path.abspath(os.path.dirname(__file__))

import json

# to_seconds_float from 
# http://stackoverflow.com/questions/1083402/missing-datetime-timedelta-toseconds-float-in-python
def to_seconds_float(timedelta):
    """Calculate floating point representation of combined
    seconds/microseconds attributes in :param:`timedelta`.

    :raise ValueError: If :param:`timedelta.days` is truthy.

        >>> to_seconds_float(datetime.timedelta(seconds=1, milliseconds=500))
        1.5
        >>> too_big = datetime.timedelta(days=1, seconds=12)
        >>> to_seconds_float(too_big) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: ('Must not have days', datetime.timedelta(1, 12))
    """
    if timedelta.days:
        raise ValueError('Must not have days', timedelta)
    return timedelta.seconds + timedelta.microseconds / 1E6

class ComparisonTimer(object):
    def __init__(self):
        self.timers = {}
    def __call__(self, name, subname, func):
        starttime = datetime.now()
        result = func()
        endtime = datetime.now()
        self.timers.setdefault(name, {})[subname] = to_seconds_float(endtime - starttime)
        return result
        
timer = ComparisonTimer()

def setupdb():
    db = Database('http://localhost:5984/test_pythonviews')
    try:
        deletedb(db)
    except: pass
    createdb(db)
    db.sync_design_doc('pythonView', os.path.join(this_directory, 'design'), language='python')
    db.sync_design_doc('javascriptView', os.path.join(this_directory, 'design'), language='javascript')
    return db

def test_doc(doc, name, count):
    print 'Testing generation of '+str(count)+' '+name+' documents.'
    db = setupdb()
    db.create([copy.copy(doc) for x in range(count)])
    py = timer(name+'_gen_'+str(count), 'python', 
                    lambda : db.views.pythonView.byType(limit=1)[0])
    js = timer(name+'_gen_'+str(count), 'js', 
                    lambda : db.views.javascriptView.byType(limit=1)[0])
    assert py == js
    print 'Testing count of '+str(count)+' '+name+' documents.'
    pyCount = timer(name+'_count_'+str(count), 'python', lambda : db.views.pythonView.count()[0])
    jsCount = timer(name+'_count_'+str(count), 'js', lambda : db.views.javascriptView.count()[0])
    assert pyCount == jsCount == count

def test_small_docs():
    for count in [10, 100, 1000, 10000, 100000]:
        test_doc({'type':'counting'}, 'small', count)
        
def test_medium_docs():
    f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'medium_size_doc.json'),'r')
    doc = json.load(f)
    for count in [10, 100, 1000, 10000, 100000]:
        test_doc(doc, 'medium', count)

def test_large_docs():
    f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'large_size_doc.json'))
    doc = json.load(f)
    for count in [10, 100, 1000, 10000]:
        test_doc(doc, 'medium', count)
    
def print_perf():
    for key in sorted(timer.timers.keys()):
        js = timer.timers[key]['js']; py = timer.timers[key]['python']
        
        if js > py:
            print key, ": Python by :",  js - py
        else:
            print key, ": Javascript by : ", py - js

if __name__ == '__main__':
    # test_small_docs()
    test_medium_docs()
    # test_large_docs()
    print_perf()