from django.shortcuts import redirect

from lib import utils
from lib.auth.firebase_auth import FirebaseAuth
from lib.managers.databases.firebase.database import FirebaseManager
from medicwhizz_web.settings import logger
from quiz.view_handlers.base import Page
from datetime import datetime


class PreQuizPage(Page):

    def __init__(self, request, mock_id):
        super().__init__(request)
        self.template_path = 'quiz/pre_quiz_page.html'
        self.mock_id = mock_id
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))
        self.user_id = self.user['localId']

    def get_view(self):
        if self.request.method == 'POST':
            if 'start_quiz' in self.request.POST:
                start_time = utils.datetime_to_timestamp(datetime.now())
                mock_test_dict = self.db.get_mock_test(self.mock_id).to_dict()
                quiz_data = {
                    'mock_id': self.mock_id,
                    'current_quiz': self.mock_id,
                    'start_time': start_time,
                    'last_updated': start_time,
                    'time_limit': mock_test_dict['duration'],
                    'num_questions': mock_test_dict['numQuestions'],
                }
                attempt_ref = self.db.init_mock_quiz(self.user_id, self.mock_id, utils.timestamp_to_datetime(start_time))
                quiz_data['quiz_state_id'] = attempt_ref.id
                self.request.session.update(quiz_data)
                return redirect('quiz:mock')
        return self.render_view()


class MockQuizPage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'quiz/mock_quiz.html'
        self.mock_id = request.session.get('mock_id')
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))
        self.user_id = self.user['localId']
        self.start_time = utils.timestamp_to_datetime(request.session.get('start_time', 0))
        self.current_question_number = request.session.get('current_question_number', 1)
        self.time_limit = float(request.session.get('time_limit', 60))
        self.num_questions = request.session.get('num_questions')
        self.quiz_state_id = request.session.get('quiz_state_id')

    def get_view(self):
        status = self.validate_session()
        if not status.is_valid:
            self.context['error'] = status.message
            if status.code == 2:  # Time is up!
                self.add_finishing_data()
                self.clear_session_quiz_data()
                return self.render_view()
            elif status.code == 1:  # INVALID MOCK QUIZ
                return redirect('quiz:home')
        if self.request.method == 'POST':
            if 'save_answer' in self.request.POST:
                return self.handle_save_answer()
            if 'change_question' in self.request.POST:
                return self.handle_change_question()
            if 'finish_quiz' in self.request.POST:
                return self.handle_finish_quiz()
        self.load_data()
        return self.render_view()

    def validate_session(self):
        logger.info(f"Session in Mock: ${dict(self.request.session)}")
        status = {'is_valid': False, 'message': '404', 'code': 0}
        if not self.request.session.get('mock_id'):
            status['message'] = 'Mock ID not found'
            status['code'] = 1
        elif self.get_time_diff() > self.time_limit:
            status['message'] = "Time's up!"
            status['code'] = 2
        else:
            status['is_valid'] = True
        return utils.dict_to_object(status)

    def get_time_diff(self):
        return (datetime.now() - self.start_time).total_seconds() / 60

    def handle_save_answer(self):
        self.update_last_updated()
        self.answer_choice(self.request.POST.get('choice'))
        if self.current_question_number == self.num_questions:  # The quiz is finished
            self.add_finishing_data()
            self.clear_session_quiz_data()
            return redirect('quiz:quiz_results', self.quiz_state_id)

        self.current_question_number += 1
        self.load_data()
        return self.render_view()

    def answer_choice(self, choice_id):
        # Get the question from session
        question_ref_string = self.request.session['current_question_dict']['id']
        question = self.db.get_document_reference(question_ref_string)

        # Get the selected choice from session
        selected_choice = None
        for choice in self.request.session['current_question_dict']['choices']:
            if choice['id'] == choice_id:
                selected_choice = choice

        # Update the database with the selected question
        self.db.answer_mock_question(
            player_id=self.user_id,
            quiz_state_id=self.quiz_state_id,
            mock_id=self.mock_id,
            index=self.current_question_number,
            question_reference=question,
            choice_reference=self.db.get_document_reference(selected_choice),
            has_scored=bool(selected_choice.get('isCorrect'))
        )

    def handle_change_question(self):
        question_number = self.request.POST.get('change_question')
        if question_number:
            self.request.session['current_question_number'] = question_number
        self.update_last_updated()
        self.load_data()
        return self.render_view()

    def load_data(self):
        question_dict = self.get_question_dict()
        context = {
            'num_questions': self.num_questions,
            'question': utils.dict_to_object(question_dict),
            'question_status': utils.dict_to_object(self.get_question_status()),
            'is_last_question': self.num_questions == self.current_question_number,
        }
        self.request.session['current_question_dict'] = question_dict
        self.context.update(context)
        self.request.session['current_question_number'] = self.current_question_number

    def get_question_dict(self):
        question = self.db.get_mock_question_from_index(self.mock_id, self.current_question_number)
        question_dict = question.to_dict()
        question_dict['id'] = question.id
        question_dict['choices'] = []
        choices_stream = self.db.get_mock_choices(self.mock_id, question.id).stream()
        for choice in choices_stream:
            choice_dict = choice.to_dict()
            choice_dict['id'] = choice.id
            question_dict['choices'].append(choice_dict)
        return question_dict

    def get_question_status(self):
        answers = []
        answers_stream = self.db.get_quiz_state_answers(self.user_id, self.mock_id, self.quiz_state_id)
        # TODO: MAINTAIN THE STATE WITHIN SESSION VARIABLE!!!!!
        for answer in answers_stream:
            answers.append({
                'number': answer.to_dict()['index'],
                'is_answered': True
            })
        for i in range(self.num_questions - len(answers)):
            answers.append({
                'number': len(answers) + 1,
                'is_answered': False
            })
        return answers

    def clear_session_quiz_data(self):
        cleared_keys = (
            'mock_id',
            'current_quiz',
            'start_time',
            'time_limit',
            'num_questions',
            'quiz_state_id',
            'current_question_number'
        )
        for key in cleared_keys:
            try:
                del self.request.session[key]
            except Exception as e:
                logger.error(e)

    def add_finishing_data(self):
        end_time = datetime.now()
        score, out_of = self.get_score()
        finishing_data = {
            'end_time': end_time,
            'elapsed_time': (end_time - self.start_time).total_seconds(),
            'score': score,
            'score_max_end': out_of
        }
        self.db.update_quiz_state(self.user_id, self.mock_id, self.quiz_state_id, finishing_data)

    def update_last_updated(self):
        try:
            timestamp = datetime.now()
            self.request.session['last_updated'] = utils.datetime_to_timestamp(timestamp)
            self.db.update_quiz_state(self.user_id, self.mock_id, self.quiz_state_id, {'lastUpdated': timestamp})
        except Exception as e:
            logger.error(f"Error during updating the last updated timestamp. {e}")

    def get_score(self):
        answers = self.db.get_mock_quiz_answers(self.user_id, self.mock_id, self.quiz_state_id)
        answers = [answer.to_dict() for answer in answers]
        score = sum(1 if answer.get('hasScored', False) else 0 for answer in answers)
        return score, len(answers)

    def handle_finish_quiz(self):
        self.add_finishing_data()
        self.clear_session_quiz_data()
        return redirect('quiz:home')
