from Akhil import settings
from medicwhizz.lib.managers.databases.firebase.db import FirebaseManager
import os

os.environ['CURRENT_ENV'] = settings.PROD_ENV
settings.CURRENT_ENV = settings.PROD_ENV
fm = FirebaseManager()

akhilez_id = 'TV6W1HjHIQOHcp5qmtuXLoW5ben2'
user_config = fm.get_user_config(akhilez_id)

