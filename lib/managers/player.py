

class Player:

    def __init__(self, player_id=None):
        self.id = player_id
        self.details = None
        self.questions_package = None

    def init_details(self, database_manager, **kwargs):
        self.id = database_manager.auth(kwargs)
        if not self.id:
            return
        user_details = database_manager.get_user_config(self.id)
        self.questions_package = user_details
        self.details = user_details

