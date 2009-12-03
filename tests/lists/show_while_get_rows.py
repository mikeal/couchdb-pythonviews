class MyListView(ListView):
    def start(self, head, request):
        return ['first chunk', request['q']], {}
    def handle_row(self, row):
        return row['key']
    def end(self):
        return 'tail'
