@show_function
def myshow(doc, request):
    return {'code':200, 'headers':{'X-Plankton':'Rusty'}, 'body':' - '.join([doc['title'],doc['body']])}
