from django.shortcuts import redirect

from lib.auth.firebase_auth import FirebaseAuth
from lib.view_handlers.base import Page
from medicwhizz_web.settings import logger


class LoginPage(Page):

    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'app/authenticate.html'
        self.firebase_auth = FirebaseAuth.get_instance()

    def get_view(self):
        if self.firebase_auth.is_authenticated(self.request.session):
            return redirect('/')
        if self.request.method == 'POST':
            if 'sign_in' in self.request.POST:
                email = self.request.POST.get('email')
                password = self.request.POST.get('password')
                firebase_auth = FirebaseAuth.get_instance()
                firebase_auth.auth_with_email(email, password)
                if firebase_auth.user is not None:
                    id_token = firebase_auth.auth_details['idToken']
                    self.request.session['id_token'] = str(id_token)
                    return redirect('/')
                else:
                    self.context['message'] = 'Login failed.'
        return self.render_view()


class SignUpPage(Page):

    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'app/sign_up.html'

    def get_view(self):
        if self.request.method == 'POST':
            if 'sign_up' in self.request.POST:
                email = self.request.POST.get('email')
                password = self.request.POST.get('password')
                self.context['message'] = str(FirebaseAuth.get_instance().create_user(email, password))
        return self.render_view()


class ResetPasswordPage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'app/forgot_password.html'

    def get_view(self):
        if self.request.method == 'POST':
            if 'reset_password' in self.request.POST:
                email = self.request.POST.get('email')
                self.context['message'] = str(FirebaseAuth.get_instance().reset_password(email))
        return self.render_view()


def handle_logout(request):
    from django.contrib import auth as django_auth
    django_auth.logout(request)
    logger.info(FirebaseAuth.get_instance().user)
    return redirect('/')
