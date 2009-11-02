class MyListView(ListView):
    def start(self, head, request):
        return ['first chunk', request['q']], {}
    def list_row(self, row):
        return row['key']
    def list_end(self):
        return 'tail'
