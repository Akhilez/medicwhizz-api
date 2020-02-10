from django.shortcuts import redirect

from lib.utils import Decorators
from quiz.view_handlers import auth_pages
from quiz.view_handlers.auth_pages import LoginPage, SignUpPage, ResetPasswordPage
from quiz.view_handlers.home_page import HomePage
from quiz.view_handlers.quiz_handler import PreQuizPage, MockQuizPage


def redirect_to_home(request):
    return redirect('/quiz/home')


@Decorators.firebase_login_required
def home(request):
    return HomePage(request).get_view()


def authenticate(request):
    return LoginPage(request).get_view()


def logout(request):
    return auth_pages.handle_logout(request)


def sign_up(request):
    return SignUpPage(request).get_view()


def reset_password(request):
    return ResetPasswordPage(request).get_view()


@Decorators.firebase_login_required
def start_quiz(request, mock_id):
    return PreQuizPage(request, mock_id).get_view()


@Decorators.firebase_login_required
def mock_quiz(request, mock_id=None):
    return MockQuizPage(request).get_view()


@Decorators.firebase_login_required
def mock_quiz_results(request, mock_id, quiz_id):
    from quiz.view_handlers.quiz_results_page import QuizResultsPage
    return QuizResultsPage(request, mock_id, quiz_id).get_view()
