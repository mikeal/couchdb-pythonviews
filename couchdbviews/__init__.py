import sys
import copy
import traceback
import inspect
import couchdb_wsgi

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

def validate_function(func):
    func._is_validate_function = True
    return func

def show_function(func):
    func._is_show_function = True
    return func
    
def wsgi_show_function(func):
    func._is_show_function = True
    func._is_wsgi_show_function = True

class EndList(Exception): pass

class ListView(object):
    _is_list_view = True
    def __init__(self, head, request, _handler):
        self.request = request
        self.head = head
        self.rows = [head]
        self.index = 0
        if 'offset' in head:
            self.offset = head['offset']
        self._handler = _handler
    
    # def start(self, head, request):
    #     return [], {'headers':{'content-type':'text/plain'}}
    # def list_row(self, row):
    #     return row
    # def list_end(self):
    #     pass

    # Not actually implemented yet
    # def list_iter(self, ):
    #     self.start({'content-type':'application/json'})
    #     for row in self.rows:
    #         yield row
    # 


        
eval_locals = {'map_function':map_function, 'reduce_function':reduce_function, 
               'rereduce_function':rereduce_function, 'validate_function':validate_function,
               'show_function':show_function, "wsgi_show_function":wsgi_show_function,
               'ListView':ListView, 'EndList':EndList}

log = open('/Users/mikeal/Documents/git/couchdb-pythonviews/test.json', 'a')
log.write('new run\n')

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
    def __init__(self, ins=sys.stdin, outs=sys.stdout, eval_locals=eval_locals):
        self.environments = {'map':{},'reduce':{},'show':{},'validate':{}}
        self.map_functions = {}
        self.reduce_functions = {}
        self.rereduce_functions = {}
        self.show_functions = {}
        self.validate_functions = {}
        self.list_views = {}
        self.current_functions = []
        self.ins = ins
        self.outs = outs
        
        self.eval_locals = eval_locals
        
        self.handler_map = {'add_fun':self.add_fun,  'map_doc':self.map_doc, 'reset':self.reset,
                            'reduce' :self.reduce_handler, 'rereduce':self.rereduce_handler,
                            'validate':self.validate_handler, 'show':self.show_handler,
                            'list':self.list_handler, 'list_row':self.list_row_handler, 
                            'list_end':self.list_end_handler}
        
    def reset(self, *args):
        # if len(args) is not 0:
        #     self.log("Got some arguments, no idea what to do with them: "+str(args))
        self.current_functions = []
        self.outs.write('true\n')
        self.outs.flush()
    
    def add_fun(self, func_string):
        if func_string not in self.map_functions:
            env = copy.copy(self.eval_locals)
            exec func_string in env
            self.environments['map'][func_string] = env
            for obj in env.values():
                if getattr(obj, '_is_map_function', None) is True:
                    self.map_functions[func_string] = obj
                if getattr(obj, '_is_list_view', None) is True and obj is not ListView:
                    self.list_views[func_string] = obj
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
        env = copy.copy(self.eval_locals)
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
    
    def show_handler(self, func_string, doc, request):
        if func_string not in self.show_functions:
            env = copy.copy(self.eval_locals)
            exec func_string in env
            self.environments['show'][func_string] = env
            for obj in env.values():
                if getattr(obj, '_is_show_function', None) is True:
                    self.show_functions[func_string] = obj
        func = self.show_functions[func_string]
        if getattr(func, '_is_wsgi_show_function', None):
            request['couchdb.document'] = doc
            r = couchdb_wsgi.CouchDBWSGIRequest(request)
            try:
                response = self.application(r.environ, r.start_response)
            except Exception, e:
                r.code = 500
                response = traceback.format_exc()
                r.headers = {'content-type':'text/plain'}

            self.output(['resp',{'code':r.code, 'body':''.join(response), 'headers':r.headers}])
        else:    
            try:
                response = func(doc, request)
            except Exception, e:
                response = {'code':500, 'body':''.join(traceback.format_exc()), 
                            'headers':{'content-type':'text/plain'}}
            if type(response) is str or type(response) is unicode:
                response = {'body':response}
            self.output(['resp',response])
    
    def validate_handler(self, func_string, new, old, user):
        if func_string not in self.validate_functions:
            env = copy.copy(self.eval_locals)
            exec func_string in env
            self.environments['validate'][func_string] = env
            for obj in env.values():
                if getattr(obj, '_is_validate_function', None) is True:
                    self.validate_functions[func_string] = obj    
        func = self.validate_functions[func_string]
        try:
            func(new, old, user)
            valid = True
        except Exception, e:
            valid = False
            response = {"error": "exception:"+str(e.__class__.__name__), "reason": [e.args, traceback.format_exc()]}
            if len(e.args) is 1:
                if type(e.args[0]) is dict:
                    response = e.args[0]
            self.outs.write(json.dumps(response)+'\n')
        if valid:
            self.outs.write('1\n')
        self.outs.flush()
    
    def list_handler(self, head, request):
        func_string = self.current_functions[0]
        v = self.list_views[func_string](head, request, self)
        self.list_view_instance = v
        response = v.start(v.head, v.request)
        if 'headers' not in response[1]:
            response[1]['headers'] = {}
        self.output(['start']+list(response))
    
    def list_row_handler(self, row):
        view = self.list_view_instance
        
        try:
            result = view.list_row(row)
            passed = True
        except EndList, e:
            passed = False
            self.output(['end', e.args])
            self.list_view_instance = None
        # TODO: Add more exception handling
        if passed:
            view.index += 1
            if hasattr(view, 'offset'):
                view.offset += 1
            if result is None:
                result = []
            elif type(result) is not list and type(result) is not tuple:
                result = [result]
            
            self.output(['chunks',result])
        
    def list_end_handler(self):
        if hasattr(self.list_view_instance, 'list_end'):
            result = self.list_view_instance.list_end()
            if result is None:
                result = []
            elif type(result) is not list and type(result) is not tuple:
                result = [result]
        else: result = []
        self.list_view_instance = None
        self.output(['end', result])
    
    def handle(self, array):
        try:
            self.handler_map[array[0]](*array[1:])
        except Exception, e:
            self.output({"error": "exception:"+str(e.__class__.__name__), "reason": [e.args, traceback.format_exc()]})
    
    def lines(self):
        line = self.ins.readline()
        while line:
            log.write(line)
            log.flush()
            yield json.loads(line)
            line = self.ins.readline()
            
    def run(self):
        self.eval_locals['log'] = self.log
        for obj in self.lines():
            self.handle(obj)
    
def run():
    CouchDBViewHandler().run()