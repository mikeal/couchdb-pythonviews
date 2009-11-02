@update_function
def myupdate(doc, request):
    doc['world'] = 'hello'
    return doc, 'hello doc'

# function(doc, req) {
#   doc.world = "hello";
#   var resp = [doc, "hello doc"];
#   return resp;
# }