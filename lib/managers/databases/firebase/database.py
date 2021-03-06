import json
from datetime import datetime
from random import randint

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import DocumentReference

from lib.managers.databases.database import DatabaseManager
from lib.managers.quiz import QuizState
from lib.utils import Decorators
from medicwhizz_web import settings
from medicwhizz_web.settings import logger


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
        self._db = firestore.client()

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

    def validate_response(self, response):
        if len(response) == 2 and isinstance(response[1], DocumentReference):
            return response[1]
        else:
            logger.error(f'Failed to add new quiz. {response}')
        return str(response)

    # ======================== Firestore methods ===========================

    # ======================== READ ONLY ===================================

    def get_document_reference(self, reference_string):
        return self._db.document(reference_string)

    def get_collection_reference(self, reference_string):
        return self._db.collection(reference_string)

    def get_user_mock_test_attempts(self, player_id, mock_id, last_n=None):
        query = self._db.collection(f'users/{player_id}/matches/{mock_id}/attempts')
        if last_n is not None:
            query = query.limit(last_n)
        return query.stream()

    def get_mock_question_from_index(self, mock_id, index):
        questions = self._db.collection(f'mockTests/{mock_id}/questions').where('index', '>=', index).limit(1).stream()
        questions_list = [question for question in questions]
        return questions_list[0]

    def is_mock_question_present(self, mock_id, index):
        # TODO: Check if this index already exists in the collection.
        return False

    def get_largest_mock_question_index(self, mock_id):
        return int(self._db.document(f'mockTests/{mock_id}').get().to_dict().get('largestQuestionIndex', 0))

    def get_mock_question(self, mock_id, question_id):
        return self._db.document(f'mockTests/{mock_id}/questions/{question_id}').get()

    def get_mock_test(self, mock_id):
        return self._db.document(f'mockTests/{mock_id}').get()

    def list_mock_tests(self):
        return self._db.collection('mockTests').order_by('index').stream()

    def get_mock_questions(self, mock_id, start_index=None, end_index=None):
        """
        :param start_index: start index
        :param end_index: one greater than the largest index requested
        :param mock_id: string
        :return: list of questions dict
        """
        query = self._db.collection(f'mockTests/{mock_id}/questions')
        if start_index is not None and end_index is not None:
            query = query.where('index', '>=', start_index) \
                .where('index', '<', end_index) \
                .order_by(u'index')
        else:
            query = query.order_by(u'index')
        questions_stream = query.stream()
        return questions_stream

    def get_admin_document(self):
        admin_docs = self._db.collection('groups').where('name', '==', 'admin')
        groups = [doc for doc in admin_docs.stream()]
        if len(groups) == 0:
            group = self.create_group(group_name='admin')
            if group is None:
                logger.error(f"Failed to create group admin")
                return None
            return group
        logger.info(f"Group = {groups[0].__dict__}")
        return groups[0].reference

    def get_largest_mock_test_index(self):
        meta_data_ref = self._db.document('metaData/mockTests')
        meta_data = meta_data_ref.get()

        if not meta_data.exists:
            meta_data_ref.update({'largestMockTestIndex': 0})
            return 0
        else:
            meta_data_dict = meta_data.to_dict()
            if 'largestMockTestIndex' not in meta_data_dict:
                meta_data_ref.update({'largestMockTestIndex': 0})
                return 0
            return int(meta_data_dict['largestMockTestIndex'])

    def get_mock_quiz_state(self, player_id, mock_id, quiz_state_id):
        return self._db.document(f'users/{player_id}/matches/{mock_id}/attempts/{quiz_state_id}').get()

    def get_user_total_num_attempts(self, player_id):
        player_details = self._db.document(f"users/{player_id}").get()
        return player_details.to_dict().get('numTotalAttempts')

    def get_running_quiz(self, player_id):
        player_details = self._db.document(f'users/{player_id}').get()
        return player_details.to_dict().get('running_quiz')

    def get_packages(self):
        return self._db.document(f'metaData/packages').get().to_dict()


    # ========================== MODIFICATIONS ================================

    def init_mock_quiz(self, player_id, mock_id, start_time):
        mock_quiz_dict = {
            'startTime': start_time,
            'lastUpdated': start_time,
            'elapsedTime': 0,
            'score': 0,
            'answers': [],
        }
        response = self._db.collection(f'users/{player_id}/matches/{mock_id}/attempts').add(mock_quiz_dict)
        if len(response) == 2 and isinstance(response[1], DocumentReference):
            try:
                self.increment_num_attempts(player_id, mock_id)
                self.init_running_quiz(player_id, mock_id, response.id)
            except Exception as e:
                logger.exception(e)
            return response[1]
        return str(response)

    def init_running_quiz(self, player_id, mock_id, quiz_state_id):
        self._db.document(f'users/{player_id}').update({
            'running_quiz': {
                'mock_id': mock_id,
                'quiz_state_id': quiz_state_id,
            }
        })

    def update_quiz_state(self, player_id, mock_id, quiz_state_id, pairs, ended=False):
        response = self._db.document(f'users/{player_id}/matches/{mock_id}/attempts/{quiz_state_id}').update(pairs)
        if ended:
            try:
                self._db.document(f'users/{player_id}').update({'running_quiz': None})
            except Exception as e:
                logger.exception(e)
        return response

    def answer_mock_question(self, player_id, quiz_state_id, mock_id, index, question_reference, choice_index,
                             has_scored):
        answer_dict = {
            'index': index,
            'questionId': question_reference,
            'hasScored': has_scored,
            'timestamp': datetime.now(),
            'chosen': choice_index,
        }
        quiz_state = self.get_mock_quiz_state(player_id, mock_id, quiz_state_id).to_dict()
        quiz_state_answers = quiz_state['answers']
        quiz_state_answers.append(answer_dict)
        response = self._db.document(
            f'users/{player_id}/matches/{mock_id}/attempts/{quiz_state_id}').update({'answers': quiz_state_answers})
        return response

    def update_mock_question_attributes(self, mock_id, question_id, pairs):
        return self._db.document(f'mockTests/{mock_id}/questions/{question_id}').update(pairs)

    def delete_mock_question(self, mock_id, question_id):
        """
        1. get all the choices and delete each
        2. delete question.
        """
        result = []
        try:
            response = self._db.document(f'mockTests/{mock_id}/questions/{question_id}').delete()
            result.append(response)
            self.increment_mock_num_questions(mock_id, -1)
        except Exception as e:
            logger.error(e)
            logger.info(f'Result of deletion = {result}')
            return e
        logger.info(f'Result of deletion = {result}')
        return result

    def delete_mock_test(self, mock_id):
        """
        1. Get all documents in mockId/questions
        2. for each question, get all choices
            a. delete each choice
            b. delete question.
        3. delete mockId document.
        :param mock_id: String
        :return: response
        """
        questions_deleted = []
        try:
            questions_stream = self._db.collection(f'mockTests/{mock_id}/questions').stream()
            for question in questions_stream:
                question.reference.delete()
                questions_deleted.append(question.id)
            self._db.document(f'mockTests/{mock_id}').delete()
            self.increment_num_mock_tests(-1)
        except Exception as e:
            logger.error(f"Error while deleting mock test {mock_id}. {e}")
            return e
        logger.info(f'Questions deleted = {questions_deleted}')
        return questions_deleted

    def add_question_to_mock_test(self, mock_id, question_text, index=None, explanation=None, choices=None,
                                  is_update=False):
        question_dict = {'text': question_text}
        if index:
            if is_update or not self.is_mock_question_present(mock_id, index):
                question_dict['index'] = index
            else:
                message = f"Mock question with index {index} already exists"
                logger.error(message)
                return message
        else:
            question_dict['index'] = self.get_largest_mock_question_index(mock_id) + 1
        if explanation:
            question_dict['explanation'] = explanation
        response = self._db.collection(f'mockTests/{mock_id}/questions').add(question_dict)
        logger.info(f"Response for adding a question {question_dict} is \n{response}")
        self.increment_mock_num_questions(mock_id, 1)
        if len(response) == 2:
            if choices:
                choices_response = self.add_choices_to_mock_question(choices, mock_id, response[1].id)
                if len(choices_response) < 2:
                    return choices_response
            return response[1]
        else:
            logger.error(f"Failed to add question. Response = {response}")
            return f'{response}'

    def add_choices_to_mock_question(self, choices, mock_id, question_id):
        # TODO: Add a choices collection to questions.
        return []

    def increment_mock_num_questions(self, mock_id, increment_value):
        self._db.document(f'mockTests/{mock_id}').update({'numQuestions': firestore.Increment(increment_value)})
        if increment_value > 0:
            self._db.document(f'mockTests/{mock_id}').update({'largestQuestionIndex': firestore.Increment(1)})

    def increment_num_mock_tests(self, increment_value):
        self._db.document(f'metaData/mockTests').update({'numMockTests': firestore.Increment(increment_value)})
        if increment_value > 0:
            self._db.document(f'metaData/mockTests').update(
                {'largestMockTestIndex': firestore.Increment(increment_value)})

    def increment_num_attempts(self, player_id, mock_id):
        match_ref = self._db.document(f"users/{player_id}/matches/{mock_id}")
        try:
            match_ref.update({'numAttempts': firestore.Increment(1)})
        except:
            match = match_ref.get()
            if match.exists:
                match_ref.update({'numAttempts': firestore.Increment(1)})
            else:
                match_ref.set({'numAttempts': 1})
        self._db.document(f"users/{player_id}").update({'numTotalAttempts': firestore.Increment(1)})

    def update_mock_quiz_attributes(self, mock_id, pairs):
        return self._db.document(f'mockTests/{mock_id}').update(pairs)

    def create_mock_test(self, name, prices, index=None, max_duration=60):
        index = index if index is not None else self.get_largest_mock_test_index() + 1
        response = self._db.collection('mockTests').add({
            'name': name,
            'price': prices,
            'index': index,
            'numQuestions': 0,
            'largestQuestionIndex': 0,
            'duration': max_duration,  # TODO: Add this max_duration from views
        })
        if len(response) > 1:
            self.increment_num_mock_tests(1)
            return response[1]
        logger.error(f"Problem creating mock_test. {response}")

    def is_user_admin(self, uid):
        logger.info(f"Checking whether user {uid} is an admin or not.")
        admin_doc = self.get_admin_document()
        user_docs = self._db.collection(f'{admin_doc.path}/users').where('uid', '==', uid)
        user_docs = [user_doc for user_doc in user_docs.stream()]
        return len(user_docs) > 0

    def create_group(self, group_name, permissions=None):
        group = {'name': group_name, 'permissions': permissions}
        response = self._db.collection('groups').add(group)
        if len(response) == 2:
            return response[1]
        logger.error(f"problem creating group {group_name}. {response}")

    @Decorators.try_and_catch
    def create_quiz(self, player_id, quiz_type):
        # TODO: Convert to where type=quiz_type query
        self._db.collection(f'users/{player_id}/matches/{quiz_type}/matches').add({
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
        # TODO: Convert to where type=quiz_type query
        state = self._db.document(f'users/{player_id}/matches/{quiz_type}/matches/{quiz_id}').get()
        return FirebaseQuizState(state)

    @Decorators.try_and_catch
    def save_quiz_state(self, state, quiz_id, player_id, quiz_type):
        # TODO: Convert to where type=quiz_type query
        self._db.document(f'users/{player_id}/matches/{quiz_type}/matches/{quiz_id}').update(state)

    @Decorators.try_and_catch
    def get_user_config(self, user_id):
        return self.set_and_get_deep_values(self._db.collection(u'users').document(user_id).get().to_dict())

    @Decorators.try_and_catch
    def get_random_question(self, start_index, end_index):
        random_index = randint(start_index, end_index)
        question = self._db.document('questions').where('position', '==', random_index).get()
        if not question.exists:
            return self.get_random_question(start_index, end_index)
        return question.to_dict()

    @Decorators.try_and_catch
    def set_and_get_default_package(self, user_id):
        package_ref = self._db.collection(u'packages').where(u'name', u'==', u'basic')
        player_ref = self._db.collection('users').document(user_id)
        package = [doc for doc in package_ref.get()][0]
        player_ref.update({'package': package.reference, 'startDate': datetime.now()})
        return self.set_and_get_deep_values(package.to_dict())

    def set_and_get_deep_values(self, collections):
        for collection_name in collections:
            value = collections[collection_name]
            if isinstance(value, DocumentReference):
                try:
                    collections[collection_name] = self.set_and_get_deep_values(
                        self._db.document('/'.join(value._path)).get().to_dict())
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
        return {collection: self.set_and_get_deep_values(self._db.collection(collection).get().to_dict())
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
            self._db.collection(collection)

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
