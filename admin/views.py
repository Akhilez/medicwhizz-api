from django.http import HttpResponse

from admin.view_handlers.admin_home import AdminHomePage


def admin_home(request):
    return AdminHomePage(request).get_view()


def add_mock(request):
    return HttpResponse("add mockkk")


def edit_mock(request, mock_test_id):
    return HttpResponse(mock_test_id)
