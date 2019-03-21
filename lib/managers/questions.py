

class QuestionManager:

    def __init__(self, database_manager, package):
        self.database_manager = database_manager
        self.package = package

    def get_question(self, index):
        return

    def get_random(self):
        return


class QuestionPackage:

    def __init__(self, num_questions, start_index=1, end_index=10):
        self.num_questions = num_questions
        self.start_index = start_index
        self.end_index = end_index
