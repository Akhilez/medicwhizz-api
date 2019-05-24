from django.http import HttpResponse

from admin.view_handlers.admin_home import AdminHomePage
from admin.view_handlers.edit_mock_test import AddMockPage, EditMockPage


def admin_home(request):
    return AdminHomePage(request).get_view()


def add_mock(request):
    return AddMockPage(request).get_view()


def edit_mock(request, mock_test_id):
    return EditMockPage(request, mock_test_id).get_view()


def edit_mock_question(request, mock_test_id, mock_test_question_id):
    return EditMockQuestionPage(request, mock_test_id, mock_test_question_id).get_view()
