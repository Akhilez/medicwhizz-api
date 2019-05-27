class Player:

    def __init__(self, player_id=None):
        self.id = player_id
        self.details = None
        self.questions_package = None

    def init_details(self, database_manager, **kwargs):
        self.id = database_manager.auth(**kwargs)
        if not self.id:
            return
        user_details = database_manager.get_user_config(self.id)
        package_with_path = user_details.get('package', database_manager.set_and_get_default_package(self.id))
        self.questions_package = package_with_path[list(package_with_path.keys())[0]]
        self.details = user_details
