class MyListView(ListView):
    def start(self, head, request):
        return ['bacon'], {}
    def list_row(self, row):
        if self.index > 1:
            raise EndList(row['key'], 'early')
        else:
            return row['key']

# function(head, req) {
#   send("bacon")
#   var row, i = 0;
#   while(row = getRow()) {
#     send(row.key);
#     i += 1;
#     if (i > 2) {
#       return('early');
#     }
#   };
# }