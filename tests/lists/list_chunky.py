class MyListView(ListView):
    def start(self, head, request):
        return ['first chunk', request['q']], {}
    def list_row(self, row):
        if self.index > 1:
            raise EndList(row['key'], 'early tail')
        else:
            return row['key']

# function(head, req) {
#   send("first chunk");
#   send(req.q);
#   var row, i=0;
#   while(row = getRow()) {
#     send(row.key);
#     i += 1;
#     if (i > 2) {
#       return('early tail');
#     }
#   };
# };