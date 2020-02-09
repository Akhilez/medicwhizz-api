from lib import utils
from lib.auth.firebase_auth import FirebaseAuth
from lib.managers.databases.firebase.database import FirebaseManager
from quiz.view_handlers.base import Page


class QuizResultsPage(Page):
    def __init__(self, request, mock_id, quiz_id):
        super().__init__(request)
        self.template_path = 'quiz/quiz_results.html'
        self.db = FirebaseManager.get_instance()
        self.user = FirebaseAuth.get_instance().initialize_user_auth_details(request.session.get('id_token'))
        self.quiz_id = quiz_id
        self.mock_id = mock_id
        self.user_id = self.user['localId']

    def get_view(self):
        self.load_data()
        return super().get_view()

    def load_data(self):
        """
        1. Get the quiz state.
        :return:
        """
        quiz_state = self.db.get_mock_quiz_state(self.user_id, self.mock_id, self.quiz_id).to_dict()
        mock_test = self.db.get_mock_test(self.mock_id).to_dict()
        questions = []
        for i in range(len(quiz_state['answers'])):
            question = quiz_state['answers'][i]['questionId'].get().to_dict()
            questions.append(question)
            quiz_state['answers'][i]['question'] = question

            chosen = quiz_state['answers'][i].get('chosen', None)
            if chosen is not None:
                for choice in question['choices']:
                    if choice['index'] == chosen:
                        choice['isChosen'] = True

        # TODO: Modify elapsedTime into minutes:seconds
        # TODO: Modify startTime-endTime into a nice string.

        self.context['quiz'] = utils.dict_to_object(quiz_state)
        self.context['mock_quiz'] = utils.dict_to_object(mock_test)



