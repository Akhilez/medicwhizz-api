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

        validity = self.check_quiz_eligibility()
        if not validity.is_valid:
            self.context['error'] = validity.message
            return self.render_view()

        if self.request.method == 'POST':
            return self.handle_post_request()

        return self.render_view()

    def handle_post_request(self):
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
                'questions': self.get_questions(),
            }
            attempt_ref = self.db.init_mock_quiz(self.user_id, self.mock_id, utils.timestamp_to_datetime(start_time))
            quiz_data['quiz_state_id'] = attempt_ref.id
            self.request.session.update(quiz_data)
            return redirect('quiz:mock')
        return self.render_view()

    def check_quiz_eligibility(self):
        """
        1. # TODO: Check if user has unlocked the quiz
        2. Check max tries
        :return:
        """
        validity = {'message': None, 'code': 0, 'is_valid': False}

        match_reference = self.db.get_document_reference(f'users/{self.user_id}/matches/{self.mock_id}')
        match_details = match_reference.get().to_dict()
        max_attempts = match_details.get('maxAttempts')
        user_attempts = match_details.get('numAttempts')
        if max_attempts is None:
            mock_reference = self.db.get_document_reference(f'mockTests/{self.mock_id}')
            max_attempts = mock_reference.get().to_dict().get('maxAttempts')
            match_reference.update({'maxAttempts': max_attempts})
        if max_attempts is not None and user_attempts is not None and user_attempts >= max_attempts:
            validity['message'] = "Your attempts have been reached maximum."
            validity['code'] = 2

        return utils.dict_to_object(validity)

    def get_questions(self):
        questions = []
        for question in self.db.get_mock_questions(self.mock_id):
            question_dict = question.to_dict()
            question_dict['id'] = question.id
            questions.append(question_dict)
        return questions


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
        self.questions = request.session.get('questions')
        if self.quiz_state_id is None:
            self.clear_session_quiz_data()

    def get_view(self):
        status = self.validate_session()
        if not status.is_valid:
            self.context['error'] = status.message
            if status.code == 2:  # Time is up!
                self.finish_quiz()
                return self.render_view()
            elif status.code == 1:  # INVALID MOCK QUIZ
                return redirect('quiz:home')
        if self.request.method == 'POST':
            if 'save_answer' in self.request.POST:
                return self.handle_save_answer()
            if any(f'change_question_{i+1}' in self.request.POST for i in range(len(self.questions))):
                return self.handle_change_question()
            if 'finish_quiz' in self.request.POST:
                return self.handle_finish_quiz()
        self.load_data()
        return self.render_view()

    def validate_session(self):
        status = {'is_valid': False, 'message': '404', 'code': 0}
        if self.request.session.get('mock_id') is None:
            status['message'] = 'Mock ID not found'
            status['code'] = 1
        elif self.get_time_diff() > self.time_limit:
            status['message'] = "Time's up!"
            status['code'] = 2
        elif self.request.session.get('quiz_state_id') is None:
            status['message'] = 'Quiz state ID not found'
            status['code'] = 1
        else:
            status['is_valid'] = True
        return utils.dict_to_object(status)

    def get_time_diff(self):
        return (datetime.now() - self.start_time).total_seconds() / 60

    def handle_save_answer(self):
        self.update_last_updated()
        self.answer_choice(int(self.request.POST.get('choice')))
        if self.current_question_number == self.num_questions:  # The quiz is finished
            self.finish_quiz()
            return redirect('quiz:mock_quiz_results', self.mock_id, self.quiz_state_id)

        self.current_question_number += 1
        self.load_data()
        return self.render_view()

    def answer_choice(self, choice_index):
        # Get the question from session
        current_question = self.questions[self.current_question_number - 1]
        question_id = current_question['id']
        question_reference = self.db.get_document_reference(f'mockTests/{self.mock_id}/questions/{question_id}')

        # Get the selected choice from session
        selected_choice = None
        for choice in current_question['choices']:
            if choice['index'] == choice_index:
                selected_choice = choice
                current_question['chosen'] = choice
                current_question['hasScored'] = bool(choice.get('isCorrect'))

        # Update the database with the selected question
        self.db.answer_mock_question(
            player_id=self.user_id,
            quiz_state_id=self.quiz_state_id,
            mock_id=self.mock_id,
            index=self.current_question_number,
            question_reference=question_reference,
            choice_index=choice_index,
            has_scored=bool(selected_choice.get('isCorrect'))
        )

    def handle_change_question(self):
        name = 'change_question_'
        for i in range(len(self.questions)):
            if name+str(i+1) in self.request.POST:
                question_number = self.request.POST.get(f'change_question_{i+1}')
                if question_number:
                    self.current_question_number = int(question_number)
                self.update_last_updated()
        else:
            self.context['error'] = "Unable to change question"
        self.load_data()
        return self.render_view()

    def load_data(self):
        question_dict = self.questions[self.current_question_number - 1]
        context = {
            'num_questions': self.num_questions,
            'question': utils.dict_to_object(question_dict),
            'question_status': utils.dict_to_object(self.get_question_status()),
            'is_last_question': self.num_questions == self.current_question_number,
        }
        self.context.update(context)
        self.request.session['current_question_number'] = self.current_question_number

    def get_question_status(self):
        answers = []
        for question in self.questions:
            answers.append({
                'number': question['index'],
                'is_answered': question.get('chosen', False)
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

    def finish_quiz(self):
        self.add_finishing_data()
        self.clear_session_quiz_data()

    def add_finishing_data(self):
        end_time = datetime.now()
        score, out_of = self.get_score()
        finishing_data = {
            'endTime': end_time,
            'elapsedTime': (end_time - self.start_time).total_seconds(),
            'score': score,
            'scoreMaxEnd': out_of
        }
        self.db.update_quiz_state(self.user_id, self.mock_id, self.quiz_state_id, finishing_data, ended=True)

    def update_last_updated(self):
        try:
            timestamp = datetime.now()
            self.request.session['last_updated'] = utils.datetime_to_timestamp(timestamp)
            self.db.update_quiz_state(self.user_id, self.mock_id, self.quiz_state_id, {'lastUpdated': timestamp})
        except Exception as e:
            logger.error(f"Error during updating the last updated timestamp. {e}")

    def get_score(self):
        score = sum(1 if question.get('hasScored', False) else 0 for question in self.request.session['questions'])
        return score, len(self.request.session['questions'])

    def handle_finish_quiz(self):
        self.finish_quiz()
        return redirect('quiz:home')
