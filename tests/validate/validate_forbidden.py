@validate_function
def myvalidate(new, old, user):
    if 'bad' in new and new['bad']:
        raise Exception({"forbidden":"bad doc"})
