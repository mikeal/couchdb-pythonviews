@show_function
def myshow(doc, request):
    return ' - '.join([doc['title'], doc['body']])
