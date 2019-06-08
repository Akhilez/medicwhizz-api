from django.shortcuts import redirect

from lib import utils
from quiz.view_handlers.base import Page
from datetime import datetime


class PreQuizPage(Page):

    def __init__(self, request, mock_id):
        super().__init__(request)
        self.template_path = 'quiz/pre_quiz_page.html'
        self.mock_id = mock_id

    def get_view(self):
        if self.request.method == 'POST':
            if 'start_quiz' in self.request.POST:
                self.request.session['current_quiz'] = self.mock_id
                self.request.session['start_time'] = utils.datetime_to_timestamp(datetime.now())
                return redirect('quiz:mock')
        return self.render_view()


class MockQuizPage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'quiz/mock_quiz.html'
        self.mock_id = request.session.get('mock_id')
        self.start_time = utils.timestamp_to_datetime(request.session.get('start_time'))
