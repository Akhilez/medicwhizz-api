import json
from datetime import datetime
from random import randint

import firebase_admin

from lib.utils import Decorators
from medicwhizz_web import settings
from medicwhizz_web.settings import logger
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1beta1 import DocumentReference
from lib.managers.databases.database import DatabaseManager
from lib.managers.quiz import QuizState


class FirebaseManager(DatabaseManager):
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if FirebaseManager.__instance is None:
            FirebaseManager()
        return FirebaseManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if FirebaseManager.__instance is not None:
            raise Exception("This class is a singleton!")
        FirebaseManager.__instance = self
        super().__init__()
        self.init_app()
        self.db = firestore.client()

    @staticmethod
    def init_app():
        try:
            firebase_admin.get_app()
        except ValueError:
            certificate_path = f'{settings.BASE_DIR}/keys/firebase_service_accounts/{settings.CURRENT_ENV}.json'
            cred = credentials.Certificate(certificate_path)
            firebase_admin.initialize_app(cred)

    def auth(self, **kwargs):
        id_token = kwargs.get('id_token')
        if id_token:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token['uid']

    @Decorators.try_and_catch
    def create_quiz(self, player_id, quiz_type):
        self.db.collection('users/' + player_id + '/matches/' + quiz_type + '/matches').add({
            'answers': [],
            'questions': [],
            'score': 0,
            'startTime': None,
            'endTime': None,
            'numQuestionsDone': 0,
            'numQuestions': 0,
            'currentQuestion': None,
            'nextQuestion': None
        })

    def is_authenticated(self, id_token):
        if id_token:
            FirebaseManager.get_instance()
            from firebase_admin import auth
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token

    @Decorators.try_and_catch
    def get_quiz_state(self, quiz_id, player_id, quiz_type):
        state = self.db.document('users/' + player_id + '/matches/' + quiz_type + '/matches/' + quiz_id).get()
        return FirebaseQuizState(state)

    @Decorators.try_and_catch
    def save_quiz_state(self, state, quiz_id, player_id, quiz_type):
        self.db.document('users/' + player_id + '/matches/' + quiz_type + '/matches/' + quiz_id).update(state)

    @Decorators.try_and_catch
    def get_user_config(self, user_id):
        return self.set_and_get_deep_values(self.db.collection(u'users').document(user_id).get().to_dict())

    @Decorators.try_and_catch
    def get_random_question(self, start_index, end_index):
        random_index = randint(start_index, end_index)
        question = self.db.document('questions').where('position', '==', random_index).get()
        if not question.exists:
            return self.get_random_question(start_index, end_index)
        return question.to_dict()

    @Decorators.try_and_catch
    def set_and_get_default_package(self, user_id):
        package_ref = self.db.collection(u'packages').where(u'name', u'==', u'basic')
        player_ref = self.db.collection('users').document(user_id)
        package = [doc for doc in package_ref.get()][0]
        player_ref.update({'package': package.reference, 'startDate': datetime.now()})
        return self.set_and_get_deep_values(package.to_dict())

    def set_and_get_deep_values(self, collections):
        for collection_name in collections:
            value = collections[collection_name]
            if isinstance(value, DocumentReference):
                try:
                    collections[collection_name] = self.set_and_get_deep_values(
                        self.db.document('/'.join(value._path)).get().to_dict())
                except Exception as exception:
                    logger.exception("Failed to get deep data. %s" % exception)
        return collections

    def dump(self):
        dump_file_path = 'medicwhizz/dumps/' + datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S') + '.json'
        collections = self.get_complete_data_as_dict()
        collections_string = json.dumps(collections)
        try:
            with open(dump_file_path, 'w') as dump_file:
                dump_file.write(collections_string)
        except Exception as exception:
            logger.exception("Error while dumping to %s. %s" % (dump_file_path, exception))

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
            logger.exception("Error while restoring from %s. %s" % (restore_source_path, exception))

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
            'extra': {  # Col
                'ID': {  # Questions ID. Doc
                    'explanation': 'explanation',
                    'attempts': 90,
                    'corrects': 60
                }
            },
            'links': {
                'ID': {
                    'accentColor': '#fff',
                    'backgroundColor': '#fff',
                    'description': 'Group Discussions',
                    'link': 'https://medicwhizz_web',
                    'linkText': "Coming Soon",
                    'position': 100,
                    'title': 'WhatsApp'
                }
            },
            'packages': {
                'ID': {
                    'name': 'basic',
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
                'ID': {  # Document  TV6W1HjHIQOHcp5qmtuXLoW5ben2
                    'matches': {  # Collection
                        'quick': {  # Document
                            'matches': {  # Collection
                                'ID': {
                                    'answers': ['/questions/ID/choices/ID'],
                                    'questions': ['/questions/ID'],
                                    'score': 1,
                                    'startTime': '1 July 2018 at 15:59:11 UTC+5:30',
                                    'endTime': '1 July 2018 at 15:59:11 UTC+5:30',
                                    'numQuestions': 0
                                }
                            },
                            'running': True,
                            'startTime': '1 July 2018 at 15:59:11 UTC+5:30',
                            'numQuestionsDone': 0,
                            'numQuestions': 0,
                            'currentQuestion': None,
                            'nextQuestion': None,
                            'answers': ['/questions/ID/choices/ID'],
                            'questions': ['/questions/ID'],
                            'score': 1
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
                    'name': 'medicwhizz_web',
                    'package': '/packages/WtLXCpAkpPHIFRhZUkaA',
                    'photoUri': 'https://lh3.googleusercontent.com/-HXbmqoCwO3M/AAAAAAAAAAI/AAAAAAAAO7M/ZJDFbi8XzVI/photo.jpg',
                    'startDate': '22 March 2019 at 01:12:32 UTC+5:30',
                    'photoPublic': False
                }
            }
        }
        return collections


class FirebaseQuizState(QuizState):
    def __init__(self, state_dict):
        super().__init__()
        self.state_dict = state_dict
