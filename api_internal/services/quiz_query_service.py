import json

from lib.auth.firebase_auth import FirebaseAuth
from lib.managers.databases.firebase.database import FirebaseManager
from api_internal.services import Service
from medicwhizz_web.settings import logger


class QuizQueryService(Service):

    def __init__(self, request):
        super().__init__(request)
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))
        self.user_id = self.user['localId']

    def get_view(self):
        user_mock_tests = self.request.session.get('user_mock_tests', None)
        if user_mock_tests is None or self.has_played_new_quizzes(user_mock_tests):
            mock_tests = self.db.list_mock_tests()
            user_mock_tests = []
            for mock_test in mock_tests:
                mock_test_dict = mock_test.to_dict()
                attempts = self.db.get_user_mock_test_attempts(self.user_id, mock_test.id, last_n=150)
                mock_test_dict['attempts'] = []
                for attempt in attempts:
                    attempt_dict = attempt.to_dict()
                    attempt_dict['id'] = attempt.id
                    attempt_dict['mock_id'] = mock_test.id
                    attempt_dict['mock_name'] = mock_test_dict['name']
                    attempt_dict['max_duration'] = mock_test_dict['duration']
                    attempt_dict = json.loads(json.dumps(attempt_dict, default=str))
                    user_mock_tests.append(attempt_dict)
            sorted(user_mock_tests, key=lambda attempt_i: attempt_i['startTime'])
            self.request.session['user_mock_tests'] = user_mock_tests

        self.context['user_mock_tests'] = user_mock_tests
        return self.render_json()

    def has_played_new_quizzes(self, user_mock_tests):
        try:
            size_of_cached_quizzes = len(user_mock_tests)
            real_attempts_size = self.db.get_user_total_num_attempts(self.user_id)
            logger.info(f"size_of_cached: {size_of_cached_quizzes}, real = {real_attempts_size}, condition = {size_of_cached_quizzes < int(real_attempts_size)}")
            return size_of_cached_quizzes < int(real_attempts_size)
        except Exception as e:
            logger.exception(e)
            if 'user_mock_tests' in self.request.session:
                del self.request.session['user_mock_tests']
            return True

