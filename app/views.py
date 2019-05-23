from django.contrib import auth as django_auth
from django.shortcuts import render_to_response, redirect, render

from lib.auth.firebase_auth import FirebaseAuth
from lib.utils import Decorators
from medicwhizz_web.settings import logger


def redirect_to_home(request):
    return redirect('/app/home')


@Decorators.firebase_login_required
def home(request):
    details = FirebaseAuth.get_instance().auth.get_account_info(request.session['id_token'])
    logger.info(str(details))
    return render_to_response(template_name='app/index.html', context={})


def authenticate(request):
    if FirebaseAuth.get_instance().is_authenticated(request.session.get('id_token')):
        return redirect('/')
    context = {}
    if request.method == 'POST':
        if 'sign_in' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')
            firebase_auth = FirebaseAuth.get_instance()
            firebase_auth.auth_with_email(email, password)
            if firebase_auth.user is not None:
                id_token = firebase_auth.user['idToken']
                request.session['id_token'] = str(id_token)
                return redirect('/')
            else:
                context['message'] = 'Login failed.'
    return render(request, template_name='app/authenticate.html', context=context)


def logout(request):
    django_auth.logout(request)
    return redirect('/')


def sign_up(request):
    context = {}
    if request.method == 'POST':
        if 'sign_up' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')
            context['message'] = str(FirebaseAuth.get_instance().create_user(email, password))
    return render(request, template_name='app/sign_up.html', context=context)


def reset_password(request):
    context = {}
    if request.method == 'POST':
        if 'reset_password' in request.POST:
            email = request.POST.get('email')
            context['message'] = str(FirebaseAuth.get_instance().reset_password(email))
    return render(request, template_name='app/forgot_password.html', context=context)
