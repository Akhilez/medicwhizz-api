from medicwhizz.lib.managers.quiz import QuickQuiz


def get_quiz_class(quiz_type):
    if quiz_type == 'quick':
        return QuickQuiz
    if quiz_type == 'full':
        return None
    return None
