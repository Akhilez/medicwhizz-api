from quiz.view_handlers.base import Page


class PreQuizPage(Page):

    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'quiz/pre_quiz_page.html'

    def get_view(self):
        return self.render_view()
