from medicwhizz_web.settings import logger


def validate_ask_request(request):
    return master_validate(request, {
        CheckTypes.POST: True,
        CheckTypes.ID_TOKEN: True,
        CheckTypes.QUIZ_TYPE: True,
        CheckTypes.QUIZ_ID: False
    })


def validate_answer_request(request):
    return master_validate(request, {
        CheckTypes.POST: True,
        CheckTypes.ID_TOKEN: True,
        CheckTypes.QUIZ_TYPE: True,
        CheckTypes.QUIZ_ID: True,
        CheckTypes.CHOICE_ID: True
    })


def validate_is_complete_request(request):
    return master_validate(request, {
        CheckTypes.POST: True,
        CheckTypes.ID_TOKEN: True,
        CheckTypes.QUIZ_TYPE: True,
        CheckTypes.QUIZ_ID: True
    })


def master_validate(request, specs):
    """
    Returns a master validity status dict
    :param request: The HttpRequest object.
    :param specs: Should be of form: {'post': True, 'id_token': False}
    :return: Format: {'is_valid': True, 'master_status': [
            {'check_type': 'post', 'is_valid': True, 'considered': True, 'data': data, 'message': message}]}
    """
    master_status = []
    for validation_check in specs:
        status = validate_from_key(validation_check, request)
        status['check_type'] = validation_check
        status['considered'] = specs[validation_check]
        master_status.append(status)
        if status['considered'] and not status['is_valid']:
            break

    is_valid = all([status['is_valid'] for status in master_status if status['considered']])
    result_status = {'is_valid': is_valid, 'master_status': master_status}
    logger.info("result_status = %s" % result_status)
    return result_status


def validate_from_key(check_type, request):
    function = CheckTypes.CHECK_TYPE_FUNCTION_MAP[check_type]
    return function(request)


def validate_post(request):
    condition = 'POST' in request.method
    return status_wrapper(condition, message='Site not available.')


def validate_id_token(request):
    id_token = request.POST.get('id_token')
    return status_wrapper(condition=id_token, message='Not authenticated.', data=id_token)


def validate_quiz_type(request):
    quiz_type = request.POST.get('quiz_type')
    return status_wrapper(condition=quiz_type, message='Quiz type invalid.', data=quiz_type)


def validate_quiz_id(request):
    quiz_id = request.POST.get('quiz_id')
    return status_wrapper(condition=quiz_id, message='Quiz ID invalid.', data=quiz_id)


def validate_choice_id(request):
    choice_id = request.POST.get('choice_id')
    return status_wrapper(condition=choice_id, message='No choice ID provided.', data=choice_id)


def status_wrapper(condition, **kwargs):
    status = {'is_valid': False}
    if condition:
        status['is_valid'] = True
        if 'data' in kwargs:
            status['data'] = kwargs.get('data')
    else:
        status['message'] = kwargs.get('message')
    return status


def get_messages_from_master_status(master_status):
    return [status.get('message') for status in master_status['master_status']]


def get_data_from_master_status(master_status):
    return {status['check_type']: status.get('data') for status in master_status['master_status']}


class CheckTypes:
    POST = 'post'
    ID_TOKEN = 'id_token'
    QUIZ_TYPE = 'quiz_type'
    QUIZ_ID = 'quiz_id'
    CHOICE_ID = 'choice_id'

    CHECK_TYPE_FUNCTION_MAP = {
        POST: validate_post,
        ID_TOKEN: validate_id_token,
        QUIZ_ID: validate_quiz_id,
        CHOICE_ID: validate_choice_id,
        QUIZ_TYPE: validate_quiz_type
    }
