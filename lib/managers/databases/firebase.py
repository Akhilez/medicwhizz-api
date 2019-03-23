import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

from medicwhizz.lib.managers.databases.database import DatabaseManager


class FirebaseManager(DatabaseManager):

    def __init__(self):
        super().__init__()
        self.init_app()
        self.db = firestore.client()

    @staticmethod
    def init_app():
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate('Akhil/serviceAccountKey.json')
            firebase_admin.initialize_app(cred)

    def auth(self, **kwargs):
        id_token = kwargs.get('id_token')
        if id_token:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token['uid']

    def get_quiz_state(self, quiz_id):
        return None

    def save_quiz_state(self, state):
        return

    def get_user_config(self, user_id):
        return None

    def get_random_question(self, start_index, end_index):
        return None
