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
                return redirect('/app/authenticate')
        return inner
