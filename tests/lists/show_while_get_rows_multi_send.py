class MyListView(ListView):
    def start(self, head, request):
        return ['bacon'], {}
    def handle_row(self, row):
        return [row['key'], 'eggs']
    def end(self):
        return 'tail'

# function(head, req) {
#     send("bacon");
#     var row;
#     log("about to getRow " + typeof(getRow));
#     while(row = getRow()) {
#         send(row.key);
#             send("eggs");
#         };
#     return "tail";
#     };