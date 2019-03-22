from medicwhizz.lib.managers.databases.firebase import FirebaseManager
from medicwhizz.lib.managers.player import Player
from medicwhizz.lib.managers.questions import QuestionManager
from medicwhizz.lib.managers.quiz import Quiz


class Handler:

    class Decorators:
        @classmethod
        def auth_required(cls, function):
            def inner(self, *args):
                if not self.player.id:
                    return 'User not authenticated'
                return function(self, *args)
            return inner

        @classmethod
        def validate_quiz_type(cls, function):
            def inner(self, quiz_type, *args):
                if not QuestionManager.get_class(quiz_type):
                    return 'Quiz type invalid.'
                return function(self, quiz_type, *args)
            return inner

        @classmethod
        def validate_quiz_id(cls, function):
            def inner(self, quiz_type, quiz_id, *args):
                # TODO: Validate quiz id
                return function(self, quiz_type, quiz_id, *args)
            return inner

    def __init__(self, id_token=None):
        self.database_manager = FirebaseManager()
        self.player = Player()
        self.player.init_details(self.database_manager, id_token=id_token)

    @Decorators.auth_required
    @Decorators.validate_quiz_type
    def ask(self, quiz_type, quiz_id):
        return self.get_quiz(quiz_type, quiz_id).ask()

    @Decorators.auth_required
    @Decorators.validate_quiz_type
    def ask_next(self, quiz_type, quiz_id):
        return self.get_quiz(quiz_type, quiz_id).ask_next()

    @Decorators.auth_required
    @Decorators.validate_quiz_type
    @Decorators.validate_quiz_id
    def is_complete(self, quiz_type, quiz_id):
        return self.get_quiz(quiz_type, quiz_id).has_completed()

    @Decorators.auth_required
    @Decorators.validate_quiz_type
    @Decorators.validate_quiz_id
    def answer(self, quiz_type, quiz_id, choice_id):
        return self.get_quiz(quiz_type, quiz_id).answer(choice_id)

    def get_quiz(self, quiz_type, quiz_id):
        question_manager = QuestionManager.get_class(quiz_type)(self.database_manager, self.player.questions_package)
        return Quiz(quiz_id, self.database_manager, question_manager)
