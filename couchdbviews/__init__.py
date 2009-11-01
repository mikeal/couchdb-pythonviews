import sys
import copy
import traceback
import inspect

# Use simplejson if it's installed because it's probably compiled with speedups
try:
    import simplejson as json
except:
    import json

class Emitter(object):
    def __init__(self):
        self.pairs = []
    def emit(self, name, value):
        # Do json serialization at emit time for better debugging
        # TODO: Add better execption handling here later
        self.pairs.append(json.dumps([name, value]))

# Properties for user defined views
def map_function(func):
    func._is_map_function = True
    return func
    
def reduce_function(func):
    func._is_reduce_function = True
    return func

def rereduce_function(func):
    func._is_rereduce_function = True
    return func

eval_locals = {'map_function':map_function, 'reduce_function':reduce_function, 
               'rereduce_function':rereduce_function,}

# log = open('/Users/mikeal/Documents/git/couchdb-pythonviews/test.json', 'w')

reduce_args_processor = {
    'rereduce':lambda x: False,
    'values': lambda x: [y[1] for y in x],
    'length': lambda x: len(x),
    'ids': lambda x: [y[0][1] for y in x],
    'keys': lambda x: [y[0][0] for y in x],
}

def get_reduce_args(func):
    spec = inspect.getargspec(func)
    if spec.keywords:
        return reduce_args_processor.keys()
    else:
        return spec.args

class CouchDBViewHandler(object):
    def __init__(self, ins=sys.stdin, outs=sys.stdout):
        self.environments = {'map':{},'reduce':{}}
        self.map_functions = {}
        self.reduce_functions = {}
        self.rereduce_functions = {}
        self.current_functions = []
        self.ins = ins
        self.outs = outs
        
        self.handler_map = {'add_fun':self.add_fun,  'map_doc':self.map_doc, 'reset':self.reset,
                            'reduce' :self.reduce_handler, 'rereduce':self.rereduce_handler}
        
    def reset(self, *args):
        # if len(args) is not 0:
        #     self.log("Got some arguments, no idea what to do with them: "+str(args))
        self.current_functions = []
        self.outs.write('true\n')
        self.outs.flush()
    
    def add_fun(self, func_string):
        if func_string not in self.map_functions:
            env = copy.copy(eval_locals)
            exec func_string in env
            self.environments['map'][func_string] = env
            for obj in env.values():
                if getattr(obj, '_is_map_function', None) is True:
                    self.map_functions[func_string] = obj
        self.current_functions.append(func_string)
        self.outs.write('true\n')
        self.outs.flush()
        
    def log(self, string):
        self.output({"log":string})
        
    def output(self, obj):
        self.outs.write(json.dumps(obj)+'\n')
        self.outs.flush()
        
    def map_doc(self, doc):
        results = []
        for func_string in self.current_functions:
            env = self.environments['map'][func_string]
            emitter = Emitter()
            env['emit'] = emitter.emit
            self.map_functions[func_string](doc)
            results.append('['+','.join(emitter.pairs)+']')
            del env['emit']
        self.outs.write('['+','.join(results)+']\n')
        self.outs.flush()
        
    def load_reduce(self, func_string):
        env = copy.copy(eval_locals)
        exec func_string in env
        self.environments['reduce'][func_string] = env
        for obj in env.values():
            if getattr(obj, '_is_reduce_function', None) is True:
                self.reduce_functions[func_string] = obj
            if getattr(obj, '_is_rereduce_function', None) is True:
                self.rereduce_functions[func_string] = obj
        if func_string not in self.rereduce_functions:
            self.rereduce_functions[func_string] = self.reduce_functions[func_string]
        self.reduce_functions[func_string]._reduce_args = get_reduce_args(self.reduce_functions[func_string])
    
    def reduce_handler(self, func_strings, reduce_args):
        results = []
        for func_string in func_strings:
            if func_string not in self.reduce_functions:
                self.load_reduce(func_string)
            r = self.reduce_functions[func_string]
            kwargs = dict([(k, reduce_args_processor[k](reduce_args),) for k in r._reduce_args])
            # TODO: Better error handling here and per result JSON serialization
            results.append(r(**kwargs))
        self.output([True, results])
        
    def rereduce_handler(self, func_strings, values):
        results = []
        for func_string in func_strings:
            if func_string not in self.rereduce_functions:
                self.load_reduce(func_string)
            r = self.rereduce_functions[func_string]
            if r._is_reduce_function:
                results.append(r(values=values, rereduce=True))
            else:
                results.append(r(values))
        self.output([True, results])
    
    def handle(self, array):
        try:
            self.handler_map[array[0]](*array[1:])
        except Exception, e:
            self.output({"error": "exception:"+str(e.__class__.__name__), "reason": [e.args, traceback.format_exc()]})
    
    def lines(self):
        line = self.ins.readline()
        while line:
            # log.write(line)
            # log.flush()
            yield json.loads(line)
            line = self.ins.readline()
            
    def run(self):
        for obj in self.lines():
            self.handle(obj)
        
    
    
def run():
    CouchDBViewHandler().run()