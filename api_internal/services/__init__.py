from abc import ABC, abstractmethod

from django.http import HttpResponse


class Service(ABC):
    def __init__(self, request):
        self.request = request
        self.context = {}

    @abstractmethod
    def get_view(self):
        return self.render_json()

    def render_json(self):
        import json
        return HttpResponse(json.dumps(self.context, default=str))
