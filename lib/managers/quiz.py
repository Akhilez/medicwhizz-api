from Akhil.settings import logger


class Quiz:

    def __init__(self, quiz_id, database_manager, question_manager):
        self.id = quiz_id
        self.question_manager = question_manager
        self.database_manager = database_manager
        self.state = self.database_manager.get_quiz_state(self.id)

    def create(self, player_id):
        quiz = self.database_manager.create_quiz(player_id)
        self.id = quiz.id
        self.state = quiz

    def ask(self):
        if self.state.num_questions_done >= self.state.num_questions:
            raise QuizException("Cannot ask more questions")

        self.state.current_question = self.question_manager.get_next_question(state=self.state)
        self.state.num_questions_done += 1
        self.state.questions.append(self.state.current_question)

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
        self.state.answers.append(choice_id)
        self.save_state()

    def save_state(self):
        self.database_manager.save_quiz_state(self.state)


class QuizException(Exception):
    def __init__(self, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)
        logger.error(message)
