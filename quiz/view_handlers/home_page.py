from lib.auth.firebase_auth import FirebaseAuth
from lib.managers.databases.firebase.database import FirebaseManager
from quiz.view_handlers.base import Page


class HomePage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'quiz/index.html'
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))

    def get_view(self):
        if self.db.is_user_admin(self.user.get('localId')):
            self.context['is_admin'] = True
        return self.render_view()

