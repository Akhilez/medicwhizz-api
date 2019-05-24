from admin.view_handlers.admin_home import AdminHomePage


def admin_home(request):
    return AdminHomePage(request).get_view()
