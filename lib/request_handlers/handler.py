from lib.managers.databases.firebase.database import FirebaseManager
from lib.managers.player import Player
from lib.managers.questions import QuestionManager
from lib.managers.quiz import Quiz


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
        return self.get_quiz(quiz_type, quiz_id).is_complete()

    @Decorators.auth_required
    @Decorators.validate_quiz_type
    @Decorators.validate_quiz_id
    def answer(self, quiz_type, quiz_id, choice_id):
        return self.get_quiz(quiz_type, quiz_id).answer(choice_id)

    def get_quiz(self, quiz_type, quiz_id):
        quiz = Quiz(
            player=self.player,
            quiz_id=quiz_id if quiz_id else self.database_manager.create_quiz(self.player.id, quiz_type),
            quiz_type=quiz_type,
            database_manager=self.database_manager
        )
        return quiz
