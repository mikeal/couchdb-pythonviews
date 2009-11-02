@filter_function
def myfilter(doc, request):
    if doc.get('good',None):
        return True

# function(doc, req) {
#   if (doc.good) {
#     return true;
#   }
# }