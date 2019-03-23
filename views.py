import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from medicwhizz.lib.request_handlers import validators
from medicwhizz.lib.request_handlers.handler import Handler


def home(request):
    return HttpResponse("Hi")


@csrf_exempt
def ask(request):
    status = validators.validate_ask_request(request)
    if not status['is_valid']:
        return HttpResponse(validators.get_messages_from_master_status(status))
    data = validators.get_data_from_master_status(status)
    return HttpResponse(json.dumps(Handler(data['id_token']).ask(data['quiz_type'], data['quiz_id'])))


def ask_next(request):
    status = validators.validate_is_complete_request(request)
    if not status['is_valid']:
        return HttpResponse(validators.get_messages_from_master_status(status))
    data = validators.get_data_from_master_status(status)
    return HttpResponse(json.dumps(Handler(data['id_token']).ask_next(data['quiz_type'], data['quiz_id'])))


def is_complete(request):
    status = validators.validate_is_complete_request(request)
    if not status['is_valid']:
        return HttpResponse(validators.get_messages_from_master_status(status))
    data = validators.get_data_from_master_status(status)
    return HttpResponse(json.dumps(Handler(data['id_token']).is_complete(data['quiz_type'], data['quiz_id'])))


def answer(request):
    status = validators.validate_answer_request(request)
    if not status['is_valid']:
        return HttpResponse(validators.get_messages_from_master_status(status))
    data = validators.get_data_from_master_status(status)
    return HttpResponse(
        json.dumps(Handler(data['id_token']).answer(data['quiz_type'], data['quiz_id'], data['choice_id'])))
