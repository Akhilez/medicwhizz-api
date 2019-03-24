from abc import ABC, abstractmethod


class DatabaseManager(ABC):

    def __init__(self):
        self.auth()

    @abstractmethod
    def auth(self, **kwargs):
        pass

    @abstractmethod
    def create_quiz(self, player_id, quiz_type):
        pass

    @abstractmethod
    def get_quiz_state(self, quiz_id, player_id, quiz_type):
        pass

    @abstractmethod
    def save_quiz_state(self, state, quiz_id, player_id, quiz_type):
        pass

    @abstractmethod
    def get_user_config(self, user_id):
        pass

    @abstractmethod
    def get_random_question(self, start_index, end_index):
        pass
