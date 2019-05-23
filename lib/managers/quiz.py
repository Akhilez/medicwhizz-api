from medicwhizz_web.settings import logger
from lib.managers.questions import QuestionManager


class Quiz:

    def __init__(self, player, quiz_id, quiz_type, database_manager):
        self.id = quiz_id
        self.database_manager = database_manager
        self.player = player
        self.question_manager = QuestionManager.get_class(quiz_type)(self.database_manager, player.questions_package)
        self.state = self.database_manager.get_quiz_state(self.id, player.id, quiz_type)

    def create(self, player_id):
        quiz = self.database_manager.create_quiz(player_id, self.question_manager)
        self.id = quiz.id
        self.state = quiz

    def ask(self):
        if self.state.num_questions_done >= self.state.num_questions:
            raise QuizException("Cannot ask more questions")

        self.state.current_question = self.question_manager.get_next_question(state=self.state)
        self.state.num_questions_done += 1
        self.state.add_question(self.state.current_question)

        logger.log(self.state.current_question)
        self.save_state()

        return self.state.current_question

    def ask_next(self):
        if self.state.num_questions_done >= self.state.num_questions:
            raise QuizException("Cannot ask more questions")

        self.state.next_question = self.question_manager.get_next_question(state=self.state)
        self.save_state()

        return self.state.next_question

    def is_complete(self):
        return self.state.num_questions == self.state.num_questions_done

    def answer(self, choice_id):
        correct_choices = [option for option in self.state.current_question.choices if option.isCorrect]
        if choice_id in correct_choices:
            self.state.score += 1
        self.state.add_answer(choice_id)
        self.save_state()

    def save_state(self):
        self.database_manager.save_quiz_state(self.state)


class QuizException(Exception):
    def __init__(self, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)
        logger.error(message)


class QuizState:
    def __init__(self):
        self.questions = []
        self.answers = []
        self.score = 0
        self.start_time = None
        self.end_time = None
        self.num_questions = 0
        self.current_question = None
        self.next_question = None

    @property
    def questions(self):
        return self.questions

    @questions.setter
    def questions(self, questions):
        self.questions = questions

    @property
    def answers(self):
        return self.answers

    @answers.setter
    def answers(self, answers):
        self.answers = answers

    @property
    def current_question(self):
        return self.current_question

    @current_question.setter
    def current_question(self, current_question):
        self.current_question = current_question

    @property
    def next_question(self):
        return self.next_question

    @next_question.setter
    def next_question(self, next_question):
        self.next_question = next_question

    def add_question(self, question):
        self.questions.append(question)

    def add_answer(self, answer):
        self.answers.append(answer)

    def to_dict(self):
        return self.__dict__
