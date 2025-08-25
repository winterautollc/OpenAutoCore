class EndpointLogger:

    @property
    def logger(self):
        return self._logger

    def __init__(self, logger):
        self._logger = logger

    def info(self, info_message):
        if self._logger:
            self._logger.info(info_message)

    def debug(self, debug_message):
        if self._logger:
            self._logger.debug(debug_message)

    def error(self, error_message, exc_info=True):
        if self._logger:
            self._logger.error(error_message, exc_info)
