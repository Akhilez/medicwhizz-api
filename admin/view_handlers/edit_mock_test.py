from django.shortcuts import redirect
from google.cloud.firestore_v1 import DocumentReference

from lib.managers.databases.firebase.database import FirebaseManager
from lib.utils import dict_to_object
from medicwhizz_web.settings import logger
from quiz.view_handlers.base import Page


class EditMockPage(Page):
    def __init__(self, request, mock_test_id):
        super().__init__(request)
        self.template_path = 'admin/edit_mock.html'
        self.mock_id = mock_test_id
        self.context['mock_id'] = mock_test_id
        self.db = FirebaseManager.get_instance()

    def get_view(self):
        self.context['mock_test_questions'] = self.get_questions()
        self.context['mock_test'] = self.get_mock_test_params()
        if self.request.method == 'POST':
            return self.handle_post_request()
        return self.render_view()

    def handle_post_request(self):
        logger.info("Handling post request")
        if 'add_new_question' in self.request.POST:
            question_text = self.request.POST.get('new_question_text')
            if question_text:
                response = self.db.add_question_to_mock_test(self.mock_id, question_text=question_text)
                if isinstance(response, DocumentReference):
                    return redirect('admin:edit_mock_question', self.mock_id, response.id)
                else:
                    self.context['error'] = f'{response}'
            else:
                self.context['error'] = 'New question text should not be empty.'
            return self.render_view()

    def get_mock_test_params(self):
        mock_test = self.db.get_mock_test(self.mock_id)
        return dict_to_object(mock_test.to_dict())

    def get_questions(self):
        questions = self.db.get_mock_questions(self.mock_id)
        questions_list = []
        for question in questions:
            question_dict = question.to_dict()
            question_dict['id'] = question.id
            questions_list.append(dict_to_object(question_dict))
            logger.info(f"Question obtained = {question_dict}")
        return questions_list


class EditMockQuestionPage(Page):
    def __init__(self, request, mock_test_id, mock_test_question_id):
        super().__init__(request)
        self.mock_id = mock_test_id
        self.question_id = mock_test_question_id
        self.template_path = 'admin/edit_mock_question.html'
        self.context['mock_id'] = mock_test_id
        self.context['question_id'] = mock_test_question_id


class AddMockPage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'admin/add_mock.html'
        self.db = FirebaseManager.get_instance()

    def get_view(self):
        if self.request.method == 'POST':
            if 'add_mock' in self.request.POST:
                name = self.request.POST.get('name')
                prices = {
                    'india': self.request.POST.get('price_india'),
                    'uk': self.request.POST.get('price_uk')
                }
                message = self.validate_parameters(name=name, prices=prices)
                if message is not None:
                    self.context['error'] = message
                else:
                    mock_doc = self.db.create_mock_test(name, prices)
                    if mock_doc:
                        return redirect('admin:edit_mock', mock_doc.id)
                    else:
                        logger.error(f"Mock id = {mock_doc}")
                        self.context['error'] = 'Error creating mock.'
        return self.render_view()

    @staticmethod
    def validate_parameters(name, prices):
        logger.info(f"Validating. name {name} and prices {prices}")
        if not name:
            return "Name of the mock test is invalid"
        try:
            for key in prices:
                prices[key] = float(prices[key])
        except ValueError:
            return "Prices are not proper."
