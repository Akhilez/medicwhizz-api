from medicwhizz.lib import utils
from medicwhizz.lib.managers.databases.firebase import FirebaseManager
from medicwhizz.lib.managers.player import Player


def ask(id_token, quiz_type, quiz_id):

    database_manager = FirebaseManager()
    player = Player()
    player.init_details(database_manager, id_token=id_token)
    if not player.id:
        return 'User not authenticated'

    quiz = utils.get_quiz_class(quiz_type)
    if not quiz:
        return 'Quiz type invalid.'

    quiz = quiz(quiz_id, database_manager, player.questions_package)
    return quiz.ask()
