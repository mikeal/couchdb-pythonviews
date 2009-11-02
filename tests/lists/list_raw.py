class MyListView(ListView):
    def start(self, head, request):
        return ['first chunk', request['q']], {}
    def list_row(self, row):
        return row['key']
    def list_end(self):
        return 'tail'

# function(head, req) {
#   send("first chunk");
#   send(req.q);
#   var row;
#   while(row = getRow()) {
#     send(row.key);
#   };
#   return "tail";
# };