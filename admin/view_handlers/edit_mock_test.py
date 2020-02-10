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
        if self.request.method == 'POST':
            return self.handle_post_request()
        self.load_data()
        return self.render_view()

    def load_data(self):
        self.context['mock_test_questions'] = self.get_questions()
        self.context['mock_test'] = self.get_mock_test_params()

    def handle_post_request(self):
        logger.info("Handling post request")
        if 'save_mock_quiz_attributes' in self.request.POST:
            return self.handle_save_attributes()
        if 'add_new_question' in self.request.POST:
            return self.handle_new_question()
        if 'delete_mock' in self.request.POST:
            return self.handle_delete_mock()
        if 'delete_mock_question' in self.request.POST:
            return self.handle_delete_mock_question()
        self.load_data()
        return self.render_view()

    def handle_delete_mock_question(self):
        question_id = self.request.POST.get('delete_mock_question_id')
        if question_id:
            response = self.db.delete_mock_question(self.mock_id, question_id)
            if isinstance(response, Exception):
                self.context['error'] = response
        else:
            self.context['error'] = 'invalid question id'
        self.load_data()
        return self.render_view()

    def handle_delete_mock(self):
        response = self.db.delete_mock_test(self.mock_id)
        if isinstance(response, Exception):
            self.context['error'] = response
            self.load_data()
            return self.render_view()
        logger.info(f'{response}')
        return redirect('admin:home')

    def handle_new_question(self):
        question_text = self.request.POST.get('new_question_text')
        if question_text:
            response = self.db.add_question_to_mock_test(self.mock_id, question_text=question_text)
            if isinstance(response, DocumentReference):
                return redirect('admin:edit_mock_question', self.mock_id, response.id)
            else:
                self.context['error'] = f'{response}'
        else:
            self.context['error'] = 'New question text should not be empty.'

        self.load_data()
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

    def handle_save_attributes(self):
        attributes = {
            'name': self.request.POST.get('name'),
            'index': int(self.request.POST.get('index', 0)),
            'duration': self.request.POST.get('duration'),
            'price': {country: self.request.POST.get(f'price_{country}') for country in ('india', 'uk')},
            'maxAttempts': self.request.POST.get('maxAttempts', 5),
        }
        self.db.update_mock_quiz_attributes(self.mock_id, attributes)
        self.context['message'] = "Saved quiz successfully."
        self.load_data()
        return self.render_view()


class EditMockQuestionPage(Page):
    def __init__(self, request, mock_test_id, mock_test_question_id):
        super().__init__(request)
        self.mock_id = mock_test_id
        self.question_id = mock_test_question_id
        self.template_path = 'admin/edit_mock_question.html'
        self.db = FirebaseManager.get_instance()

        self.context['mock_id'] = mock_test_id
        self.context['question_id'] = mock_test_question_id

    def get_view(self):
        if self.request.method == 'POST':
            return self.handle_post_request()
        self.load_data()
        return self.render_view()

    def load_data(self):
        self.context['question'] = dict_to_object(self.db.get_mock_question(self.mock_id, self.question_id).to_dict())

    def handle_post_request(self):
        if 'save_details' in self.request.POST:
            return self.handle_save()
        if 'delete_mock_question' in self.request.POST:
            return self.handle_delete_question()
        if 'add_new_question' in self.request.POST:
            return EditMockPage(self.request, self.mock_id).handle_new_question()
        self.context['error'] = "Couldn't handle the request"
        self.load_data()
        return self.render_view()

    def handle_delete_question(self):
        response = self.db.delete_mock_question(self.mock_id, self.question_id)
        if isinstance(response, Exception):
            self.context['error'] = response
            self.load_data()
            return self.render_view()
        return redirect('admin:edit_mock', self.mock_id)

    def handle_save(self):
        attributes = {
            'text': self.request.POST.get('question_text'),
            'index': int(self.request.POST.get('question_index', 0)),
            'explanation': self.request.POST.get('explanation'),
            'choices': self.get_choices_from_html(),
        }
        self.db.update_mock_question_attributes(self.mock_id, self.question_id, attributes)
        self.context['message'] = "Question saved successfully."
        self.load_data()
        return self.render_view()

    def get_choices_from_html(self):
        choice_ids = []
        for key in self.request.POST:
            if 'choice-' in key:
                choice_ids.append(key[7:])
        logger.info(f"Choice Ids found = {choice_ids}")
        choices = []
        for choice_id in choice_ids:
            choice_text = self.request.POST.get(f'choice-{choice_id}')
            if len(choice_text) == 0:
                continue
            choices.append({
                'index': int(self.request.POST.get(f'choiceIndex-{choice_id}', 0)),
                'text': choice_text,
                'isCorrect': bool(self.request.POST.get(f'is_correct_{choice_id}', False)),
            })
        return choices


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
