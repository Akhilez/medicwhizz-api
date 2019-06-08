from django.shortcuts import redirect

from lib import utils
from lib.auth.firebase_auth import FirebaseAuth
from lib.managers.databases.firebase.database import FirebaseManager
from quiz.view_handlers.base import Page
from datetime import datetime


class PreQuizPage(Page):

    def __init__(self, request, mock_id):
        super().__init__(request)
        self.template_path = 'quiz/pre_quiz_page.html'
        self.mock_id = mock_id
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))

    def get_view(self):
        if self.request.method == 'POST':
            if 'start_quiz' in self.request.POST:
                start_time = utils.datetime_to_timestamp(datetime.now())
                quiz_data = {
                    'current_quiz': self.mock_id,
                    'start_time': start_time,
                    'time_limit': self.get_mock_time_limit(),
                    'num_questions': self.get_num_questions(),
                    'quiz_state_id': self.add_quiz_to_db(start_time),
                }
                self.request.session.update(quiz_data)
                return redirect('quiz:mock')
        return self.render_view()

    def add_quiz_to_db(self, start_time):
        quiz_reference = self.db.init_mock_quiz(self.user['localId'], self.mock_id, start_time)
        return quiz_reference.id

    def get_num_questions(self):
        return self.db.get_mock_questions_reference(self.mock_id).get().size

    def get_mock_time_limit(self):
        mock_test = self.db.get_mock_test()
        return mock_test['duration']


class MockQuizPage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'quiz/mock_quiz.html'
        self.mock_id = request.session.get('mock_id')
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))
        self.start_time = utils.timestamp_to_datetime(request.session.get('start_time'))
        self.current_question_number = request.session.get('current_question_number', 0)
        self.time_limit = request.session.get('time_limit')
        self.num_questions = request.session.get('num_questions')
        self.quiz_state_id = request.session.get('quiz_state_id')

    def get_view(self):
        status = self.validate_session()
        if not status.is_valid:
            self.context['error'] = status.message
            return self.render_view()
        if self.request.method == 'POST':
            if 'save_answer' in self.request.POST:
                return self.handle_save_answer()
            if 'change_question' in self.request.POST:
                return self.handle_change_question()
        self.load_data()
        return self.render_view()

    def validate_session(self):
        status = utils.dict_to_object({'is_valid': False, 'message': '404'})
        if not self.request.session.get('mock_id'):
            status.message = 'Mock ID not found'
        elif self.get_time_diff() > self.time_limit():
            status.message = "Time's up!"
        else:
            status.is_valid = True
        return status

    def get_time_diff(self):
        return (datetime.now() - self.start_time).total_seconds()

    def handle_save_answer(self):
        self.answer_choice(self.request.POST.get('choice'))
        self.current_question_number += 1
        self.load_data()
        return self.render_view()

    def answer_choice(self, choice_id):
        question = self.db.get_mock_question_from_index(self.current_question_number)
        choice = self.db.get_mock_choice(self.mock_id, question.id, choice_id)
        self.db.answer_mock_question(
            player_id=self.user['localId'],
            quiz_state_id=self.quiz_state_id,
            mock_id=self.mock_id,
            index=self.current_question_number,
            question_id=question.id,
            question_reference=question.reference,
            choice_reference=choice.refernce,
            is_correct=choice.get('isCorrect', False)
        )

    def handle_change_question(self):
        # TODO: Handle change question
        self.load_data()
        return self.render_view()

    def load_data(self):
        self.request.session['last_updated'] = utils.datetime_to_timestamp(datetime.now())
        self.context['question_status'] = self.get_question_status()

    def get_question_status(self):
        # TODO: Get the question status from db
        return []
