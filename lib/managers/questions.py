from abc import ABC, abstractmethod

RANDOM = 'quick'
ALL = 'full'


class QuestionManager(ABC):

    def __init__(self, database_manager, package):
        self.database_manager = database_manager
        self.package = package

    @abstractmethod
    def get_next_question(self, state, **kwargs):
        pass

    @staticmethod
    def get_class(strategy=RANDOM):
        if strategy == RANDOM:
            return RandomQuestionManager


class RandomQuestionManager(QuestionManager):

    def __init__(self, database_manager, package):
        super().__init__(database_manager, package)
        self.type = RANDOM

    def get_next_question(self, state, **kwargs):
        return self.get_random_question_excluding(state.questions)

    def get_random_question_excluding(self, questions):
        while True:  # TODO: Improve the get_random logic
            question = self.database_manager.get_random_question(self.package['startIndex'], self.package['endIndex'])
            if question not in questions:
                return question


class AllQuestionManager(QuestionManager):

    def get_next_question(self, state, **kwargs):
        last_question = state.questions[-1]
        next_question = self.database_manager.get_next_question(last_question)
        return next_question


class QuestionPackage:

    def __init__(self, num_questions, start_index=1, end_index=10):
        self.num_questions = num_questions
        self.start_index = start_index
        self.end_index = end_index
