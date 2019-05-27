import pyrebase

from keys import credentials
from lib.managers.databases.firebase.database import FirebaseManager
from medicwhizz_web.settings import logger, CURRENT_ENV, DEV_ENV, PROD_ENV


class FirebaseAuth:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if FirebaseAuth.__instance is None:
            FirebaseAuth()
        return FirebaseAuth.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if FirebaseAuth.__instance is not None:
            raise Exception("This class is a singleton!")
        FirebaseAuth.__instance = self
        self.firebase_app = self.initialize_firebase_app()
        self.auth = self.firebase_app.auth()
        self.auth_details = None
        self.user = None

    def auth_with_email(self, email, password):
        try:
            logger.info(f'User before login = {self.user}')
            self.auth_details = self.auth.sign_in_with_email_and_password(email, password)
            logger.info(f"Login response = {self.auth_details}")
            self.initialize_user_auth_details(self.auth_details['idToken'])
            logger.info(f'User after login = {self.user}')
            return True
        except Exception as e:
            logger.info(f"Login failed for email {email}. {e}")
            return False

    def is_authenticated(self, session):
        id_token = session.get('id_token')
        if id_token:
            try:
                return self.is_authenticated_and_email_verified(id_token) or \
                       self.is_authenticated_and_email_verified(self.refresh_id_token(id_token))
            except Exception as e:
                logger.error(e)
        return False

    def is_authenticated_and_email_verified(self, id_token):
        is_auth = FirebaseManager.get_instance().is_authenticated(id_token)
        if is_auth:
            self.user = self.initialize_user_auth_details(id_token)
            return self.user['emailVerified']

    def refresh_id_token(self, id_token):
        self.auth_details = self.auth.refresh(id_token)
        return self.auth_details['idToken']

    def initialize_user_auth_details(self, id_token):
        """
        :param id_token: id_token
        :return: dict : {'localId': 'LIaDqg1YISPR0Qg22ibq9g5TAgH3', 'email': 'lightrescuer@gmail.com',
             'passwordHash': 'UkVEQUNURUQ=', 'emailVerified': True, 'passwordUpdatedAt': 1558621724112,
             'providerUserInfo': [
                 {'providerId': 'password', 'federatedId': 'lightrescuer@gmail.com', 'email': 'lightrescuer@gmail.com',
                  'rawId': 'lightrescuer@gmail.com'}], 'validSince': '1558621724', 'lastLoginAt': '1558682989858',
             'createdAt': '1558621724112'}
        """
        try:
            logger.info(f'user = {self.user}')
            if self.user is None:
                self.user = self.auth.get_account_info(id_token)['users'][0]
                logger.info(f'new user details = {self.user}')
        except Exception as e:
            logger.error(e)
        return self.user

    def create_user(self, email, password):
        if email and password:
            try:
                self.user = self.auth.create_user_with_email_and_password(email, password)
                self.auth.send_email_verification(self.user['idToken'])
                logger.info(f'{self.user}')
                return 'Successful. Verify your email id.'
            except Exception as e:
                logger.error(e)
                return e

    def reset_password(self, email):
        if email:
            try:
                self.auth.send_password_reset_email(email)
                return 'Please check your email to reset your password.'
            except Exception as e:
                logger.error(e)
                return e

    @staticmethod
    def initialize_firebase_app():
        if CURRENT_ENV == DEV_ENV:
            return pyrebase.initialize_app(credentials.dev_credentials)
        elif CURRENT_ENV == PROD_ENV:
            return pyrebase.initialize_app(credentials.prod_credentials)
        else:
            logger.error("Current env is not set.")

        FirebaseManager.get_instance()
