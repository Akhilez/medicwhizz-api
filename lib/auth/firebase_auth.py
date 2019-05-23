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
        self.user = None

    def auth_with_email(self, email, password):
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
            return True
        except:
            logger.info(f"Login failed for email {email}")
            return False

    def is_authenticated(self, id_token):
        if id_token:
            try:
                is_auth = FirebaseManager.get_instance().is_authenticated(id_token)
                return is_auth and self.auth.get_account_info(id_token)['users'][0]['emailVerified']
            except Exception as e:
                logger.error(e)
                return False

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
