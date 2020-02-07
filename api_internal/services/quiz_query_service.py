from lib.auth.firebase_auth import FirebaseAuth
from lib.managers.databases.firebase.database import FirebaseManager


class QuizQueryService:

    def __init__(self, request):
        self.request = request
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))

    def get_user_quizzes(self):
        mock_tests = self.db.get_user_mock_test_attempts(last_n=3)
        return

