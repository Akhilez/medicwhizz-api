from quiz.view_handlers.base import Page


class AdminHomePage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'admin/admin_home.html'
