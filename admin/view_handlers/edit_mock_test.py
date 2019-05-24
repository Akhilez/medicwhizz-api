from django.shortcuts import redirect

from lib.managers.databases.firebase.database import FirebaseManager
from medicwhizz_web.settings import logger
from quiz.view_handlers.base import Page


class EditMockPage(Page):
    def __init__(self, request, mock_test_id):
        super().__init__(request)
        self.template_path = 'admin/edit_mock.html'
        self.mock_id = mock_test_id
        self.context['mock_id'] = mock_test_id

    def get_view(self):
        # TODO: Get the questions
        return self.render_view()


class EditMockQuestionPage(Page):
    def __init__(self, request, mock_test_id, mock_test_question_id):
        super().__init__(request)
        self.mock_id = mock_test_id
        self.question_id = mock_test_question_id
        self.template_path = ''
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
