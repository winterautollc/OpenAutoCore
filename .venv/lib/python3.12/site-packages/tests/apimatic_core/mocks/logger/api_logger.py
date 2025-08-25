
class ApiLogger():

    @property
    def logged_messages(self):
        return self._logged_messages

    def __init__(self):
        self._logged_messages = []

    def info(self, info_message):
        self._logged_messages.append(info_message)

    def debug(self, debug_message):
        self._logged_messages.append(debug_message)

    def error(self, error_message, exc_info):
        self._logged_messages.append('{}-{}'.format(error_message, exc_info))
