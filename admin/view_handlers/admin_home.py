from lib.managers.databases.firebase.database import FirebaseManager
from lib.utils import dict_to_object
from quiz.view_handlers.base import Page


class AdminHomePage(Page):
    def __init__(self, request):
        super().__init__(request)
        self.template_path = 'admin/admin_home.html'
        self.db = FirebaseManager.get_instance()

    def get_view(self):
        self.context['mock_tests'] = self.get_mock_tests()
        self.context['packages'] = self.db.get_packages()
        return self.render_view()

    def get_mock_tests(self):
        mock_tests_snapshots = self.db.list_mock_tests()
        mock_tests = []
        for mock_test in mock_tests_snapshots:
            test_dict = mock_test.to_dict()
            test_dict['id'] = mock_test.id
            mock_tests.append(dict_to_object(test_dict))
        return mock_tests
