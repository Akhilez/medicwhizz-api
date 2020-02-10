from lib.auth.firebase_auth import FirebaseAuth
from lib.managers.databases.firebase.database import FirebaseManager
from quiz.view_handlers.base import Page


class HomePage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'quiz/index.html'  # index.html'
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))
        self.user_id = self.user['localId']

    def get_view(self):
        if self.db.is_user_admin(self.user_id):
            self.context['is_admin'] = True
        self.context['mock_tests'] = self.get_mock_tests()
        return self.render_view()

    def get_mock_tests(self):
        mock_tests_list = []
        tests = self.db.list_mock_tests()
        running_quiz_id = self.check_running_quizzes()
        for test in tests:
            test_dict = test.to_dict()
            test_dict['id'] = test.id
            test_dict['locked'] = self.is_test_locked()
            test_dict['local_price'] = self.get_local_price(test_dict['price'])
            test_dict['local_country'] = 'India'  # TODO: Get the country of the user
            if running_quiz_id == test.id:
                test_dict['running'] = True
            mock_tests_list.append(test_dict)
        return mock_tests_list

    def is_test_locked(self):
        return True  # TODO: Get this from user's purchase info

    def get_local_price(self, price_dict):
        return price_dict['india']  # TODO: Get the country of user

    def check_running_quizzes(self):
        if self.request.session.get('quiz_state_id') is None:
            running_quiz_details = self.db.get_running_quiz(self.user_id)
            if running_quiz_details is not None:
                self.request.session.update(running_quiz_details)
        return self.request.session.get('mock_id')
