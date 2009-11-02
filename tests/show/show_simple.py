@show_function
def myshow(doc, request):
    log('ok')
    return ' - '.join([doc['title'], doc['body']])
