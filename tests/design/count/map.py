@map_function
def mymap(doc):
    emit(doc['_id'], 1)