import firebase_admin
from Akhil.settings import logger
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1beta1 import DocumentReference, CollectionReference
from firebase_admin import auth
from datetime import datetime
from random import randint
import json
from Akhil import settings

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
            certificate_path = f'{settings.BASE_DIR}/{settings.PROJECT_NAME}/firebase_service_accounts/{settings.CURRENT_ENV}.json'
            cred = credentials.Certificate(certificate_path)
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
            if deep:
                self.set_and_get_deep_values(player_config)
        except Exception as exception:
            logger.error(f"Error in getting player config {exception}")
        return player_config

    def get_random_question(self, start_index, end_index):
        random_index = randint(start_index, end_index)
        question = self.db.document('questions').where('position', '==', random_index).get()
        if not question.exists:
            return self.get_random_question(start_index, end_index)
        return question.to_dict()

    def set_and_get_default_package(self, user_id):
        """
        1. Get the default package.
        2. Set the question reference to the user.
        3. Return the package dict
        :param deep: Check if the deep data is needed.
        :param user_id: uid
        :return: package dict - {'packages/ID': {'startIndex': 1 ...}}
        """
        try:
            package_ref = self.db.collection(u'packages').where(u'name', u'==', u'basic')
            player_ref = self.db.collection('users').document(user_id)
            package = [doc for doc in package_ref.get()][0]
            self.set_player_attributes(player_ref, package=package.reference, startDate=datetime.now())
            return self.set_and_get_deep_values(package.to_dict())
        except Exception as exception:
            logger.exception(f"Failed to set and get default package. {exception}")

    @staticmethod
    def set_player_attributes(player_ref, **kwargs):
        try:
            player_ref.update(kwargs)
        except Exception as exception:
            logger.exception(f"Failed to set player attributes{kwargs}. {exception}")

    def set_and_get_deep_values(self, values):
        for key in values:
            value = values[key]
            if isinstance(value, DocumentReference):
                try:
                    values[key] = self.set_and_get_deep_values(self.db.document('/'.join(value._path)).get().to_dict())
                except Exception as exception:
                    logger.exception(f"Failed to get deep data. {exception}")
        return values

    def dump(self):
        dump_file_path = 'medicwhizz/dumps/' + datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S') + '.json'
        collections = self.get_complete_data_as_dict()
        collections_string = json.dumps(collections)
        try:
            with open(dump_file_path, 'w') as dump_file:
                dump_file.write(collections_string)
        except Exception as exception:
            logger.exception(f"Error while dumping to {dump_file_path}. {exception}")

    def get_complete_data_as_dict(self):
        return {collection: self.set_and_get_deep_values(self.db.collection(collection).get().to_dict())
                for collection in list(self.get_schema().keys())}

    def restore_from_file(self, restore_source_path):
        try:
            with open(restore_source_path, 'r') as restore_file:
                collections = json.loads(restore_file.read())
                for collection in collections:
                    self.restore(collection, [collection])
        except Exception as exception:
            logger.exception(f"Error while restoring from {restore_source_path}. {exception}")

    def restore(self, collections, path):
        for collection in collections:
            """
            create collection
            for each document:
                
            """
            self.db.collection(collection)

    @staticmethod
    def get_schema():
        collections = {
            'explanations': {  # Col
                'ID': {  # Questions ID. Doc
                    'explanation': 'explanation'
                }
            },
            'links': {
                'ID': {
                    'accentColor': '#fff',
                    'backgroundColor': '#fff',
                    'description': 'Group Discussions',
                    'link': 'https://akhilkanna.in',
                    'linkText': "Coming Soon",
                    'position': 100,
                    'title': 'WhatsApp'
                }
            },
            'packages': {
                'basic': {
                    'duration': 365,
                    'endIndex': 300,
                    'price': 2.5,
                    'startIndex': 1
                }
            },
            'questions': {  # Col
                'ID': {  # Doc
                    'choices': {  # Col
                        'ID': {  # Doc
                            'choice': 'Option 1',
                            'isCorrect': False
                        }
                    },
                    'position': 818,
                    'question': 'question?'
                }
            },
            'reports': {
                'ID': {
                    'datetime': '1 July 2018 at 15:59:11 UTC+5:30',
                    'message': 'message',
                    'question': '/question/ID',
                    'user': 'ID'
                }
            },
            'users': {  # Collection
                'TV6W1HjHIQOHcp5qmtuXLoW5ben2': {  # Document
                    'matches': {  # Collection
                        'quick': {  # Document
                            'matches': {  # Collection
                                'ID': {
                                    'answers': ['/questions/ID/choices/ID'],
                                    'questions': ['/questions/ID'],
                                    'score': 1,
                                    'startTime': '1 July 2018 at 15:59:11 UTC+5:30'
                                }
                            }
                        },
                        'full': {  # Document
                            'answers': ['/questions/ID/choices/ID'],
                            'questions': ['/questions/ID'],
                            'elapsedTime': 160,
                            'fullIndex': 43,
                            'score': 6,
                            'startTime': '1 July 2018 at 15:59:11 UTC+5:30'
                        }
                    },
                    'level': 1.3,
                    'name': 'Akhilez',
                    'package': '/packages/WtLXCpAkpPHIFRhZUkaA',
                    'photoUri': 'https://lh3.googleusercontent.com/-HXbmqoCwO3M/AAAAAAAAAAI/AAAAAAAAO7M/ZJDFbi8XzVI/photo.jpg',
                    'startDate': '22 March 2019 at 01:12:32 UTC+5:30'
                }
            }
        }
        return collections
