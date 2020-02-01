from lib.auth.firebase_auth import FirebaseAuth
from lib.managers.databases.firebase.database import FirebaseManager
from quiz.view_handlers.base import Page


class QuizResultsPage(Page):
    def __init__(self, request, quiz_id):
        super().__init__(request)
        self.template_path = 'quiz/quiz_results.html'
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))
        self.quiz_id = quiz_id

    def get_view(self):
        return super().get_view()

