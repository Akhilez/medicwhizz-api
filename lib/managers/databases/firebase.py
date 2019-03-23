import firebase_admin
from Akhil.settings import logger
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1beta1 import DocumentReference, CollectionReference
from firebase_admin import auth
from datetime import datetime
from random import randint

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

    def get_user_config(self, user_id, deep=True):
        player_config = {}
        doc_ref = self.db.collection(u'users').document(user_id)
        try:
            player_config = doc_ref.get().to_dict()
            self.set_deep_values(player_config)
        except Exception as exception:
            logger.error(f"Error in getting player config {exception}")
        return player_config

    def get_random_question(self, start_index, end_index):
        random_index = randint(start_index, end_index)
        question = self.db.document('questions').where('position', '==', random_index).get()
        if not question.exists:
            return self.get_random_question(start_index, end_index)
        return question.to_dict()

    def set_and_get_default_package(self, user_id, deep=True):
        """
        1. Get the default package.
        2. Set the question reference to the user.
        3. Return the package dict
        :param deep: Check if the deep data is needed.
        :param user_id: uid
        :return: package dict
        """
        try:
            package_ref = self.db.collection(u'packages').where(u'name', u'==', u'basic')
            player_ref = self.db.collection('users').document(user_id)

            self.set_player_attributes(player_ref, package=package_ref, startDate=datetime.now())

            package = package_ref.get().to_dict()
            if deep:
                self.set_deep_values(package)

            return package
        except Exception as exception:
            logger.exception(f"Failed to set and get default package. {exception}")

    @staticmethod
    def set_player_attributes(player_ref, **kwargs):
        try:
            player_ref.update(kwargs)
        except Exception as exception:
            logger.exception(f"Failed to set player attributes{kwargs}. {exception}")

    def set_deep_values(self, values):
        for key in values:
            value = values[key]
            if isinstance(value, dict):
                return self.set_deep_values(value)
            if isinstance(value, DocumentReference):
                reference_getter = self.db.document
            elif isinstance(value, CollectionReference):
                reference_getter = self.db.collection
            else:
                return

            try:
                snapshot = reference_getter(value._path).get()
                values[key] = snapshot.to_dict()
                self.set_deep_values(values[key])
                values[key]['snapshot'] = snapshot
            except Exception as exception:
                logger.exception(f"Failed to get deep data. {exception}")
