from abc import ABC

from django.shortcuts import render


class Page(ABC):
    def __init__(self, request):
        self.context = {}
        self.request = request
        self.template_path = 'app/index.html'

    def get_view(self):
        return self.render_view()

    def render_view(self):
        return render(self.request, template_name=self.template_path, context=self.context)
