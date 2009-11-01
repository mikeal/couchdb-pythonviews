# Make sure the first function isn't used
def first_function(): pass

@map_function
def mymap(doc):
    if 'type' in doc:
        emit(doc['type'], doc)

# Make sure the last function isn't used instead of mymap
def another_function(): pass
