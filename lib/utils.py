from medicwhizz_web.settings import logger


class Decorators:
    @classmethod
    def try_and_catch(cls, function):
        def inner(*args):
            try:
                function(*args)
            except Exception as exception:
                logger.exception(exception)
        return inner

    @classmethod
    def firebase_login_required(cls, function):
        def inner(request, *args):
            from lib.auth.firebase_auth import FirebaseAuth
            if FirebaseAuth.get_instance().is_authenticated(request.session):
                return function(request, *args)
            else:
                from django.shortcuts import redirect
                return redirect('/quiz/authenticate')
        return inner


def dict_to_object(data):
    """
    Converts a dictionary to objects
    :param data: dict
    :return: obj (named tuple)
    """
    import json
    return json.loads(json.dumps(data), object_hook=_json_object_hook)


def _json_object_hook(d):
    from collections import namedtuple
    return namedtuple('node', d.keys())(*d.values())


def datetime_to_timestamp(date_time):
    from datetime import datetime
    return str(datetime.timestamp(date_time))


def timestamp_to_datetime(timestamp):
    """
    :param timestamp: "1545730073.46456"
    :return: datetime object
    """
    from datetime import datetime
    return datetime.fromtimestamp(float(timestamp))
