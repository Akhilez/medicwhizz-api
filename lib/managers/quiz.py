from abc import ABC, abstractmethod

from Akhil.settings import logger
from medicwhizz.lib.managers.questions import QuestionManager


class Quiz(ABC):

    def __init__(self, quiz_id, database_manager, questions_package):
        self.id = quiz_id
        self.question_manager = QuestionManager(database_manager, questions_package)
        self.database_manager = database_manager
        self.state = self.database_manager.get_quiz_state(self.id)

    @abstractmethod
    def ask(self, **kwargs):
        pass

    @abstractmethod
    def ask_next(self):
        pass

    @abstractmethod
    def is_completed(self):
        pass

    @abstractmethod
    def answer(self, choice):
        pass


class QuickQuiz(Quiz):  # TODO: Move quiz question logic to question manager.

    def ask(self, **kwargs):
        if self.state.num_questions_done >= self.state.num_questions:
            raise QuizException("Cannot ask more questions")

        self.state.current_question = self.get_random_question()
        self.state.num_questions_done += 1
        self.state.questions.append(self.state.current_question)

        logger.log(self.state.current_question)
        self.save_state()

        return self.state.current_question

    def ask_next(self):
        if self.state.num_questions_done >= self.state.num_questions:
            raise QuizException("Cannot ask more questions")

        self.state.next_question = self.get_random_question()
        self.save_state()

    def is_completed(self):
        return self.state.num_questions == self.state.num_questions_done

    def get_random_question(self):
        while True:  # TODO: Improve the get_random logic
            question = self.question_manager.get_random()
            if question not in self.state.questions:
                return question

    def answer(self, choice):
        correct_choices = [option for option in self.state.current_question.choices if option.isCorrect]
        if choice in correct_choices:
            self.state.score += 1
        self.state.answers.append(choice)
        self.save_state()

    def save_state(self):
        self.database_manager.save_quiz_state(self.state)


class QuizException(Exception):
    def __init__(self, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)
        logger.error(message)
