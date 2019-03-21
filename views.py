import json
from django.http import HttpResponse, Http404

from medicwhizz.lib.request_handlers import ask as ask_handler


def home(request):
    return HttpResponse("Hi")


def ask(request):
    if 'POST' not in request.method:
        raise Http404

    id_token = request.POST.get('id_token')
    if not id_token:
        return HttpResponse('Not authenticated')

    quiz_type = request.POST.get('quiz_type')
    if not quiz_type:
        return HttpResponse('Quiz type invalid')

    quiz_id = request.POST.get('quiz_id')

    return HttpResponse(json.dumps(ask_handler.ask(id_token, quiz_type, quiz_id)))
