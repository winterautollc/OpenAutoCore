from apimatic_core.configurations.endpoint_configuration import EndpointConfiguration
from apimatic_core.configurations.global_configuration import GlobalConfiguration
from apimatic_core.logger.endpoint_logger import EndpointLogger
from apimatic_core.response_handler import ResponseHandler


class ApiCall:

    @property
    def new_builder(self):
        return ApiCall(self._global_configuration, logger=self._endpoint_logger.logger)

    def __init__(
            self,
            global_configuration=GlobalConfiguration(),
            logger=None
    ):
        self._global_configuration = global_configuration
        self._request_builder = None
        self._response_handler = ResponseHandler()
        self._endpoint_configuration = EndpointConfiguration()
        self._endpoint_logger = EndpointLogger(logger)
        self._endpoint_name_for_logging = None

    def request(self, request_builder):
        self._request_builder = request_builder
        return self

    def response(self, response_handler):
        self._response_handler = response_handler
        return self

    def endpoint_configuration(self, endpoint_configuration):
        self._endpoint_configuration = endpoint_configuration
        return self

    def endpoint_name_for_logging(self, endpoint_name_for_logging):
        self._endpoint_name_for_logging = endpoint_name_for_logging
        return self

    def execute(self):
        try:
            _http_client_configuration = self._global_configuration.get_http_client_configuration()

            if _http_client_configuration.http_client is None:
                raise ValueError("An HTTP client instance is required to execute an Api call.")

            _http_request = self._request_builder \
                .endpoint_logger(self._endpoint_logger) \
                .endpoint_name_for_logging(self._endpoint_name_for_logging) \
                .build(self._global_configuration)

            _http_callback = _http_client_configuration.http_callback

            self.update_http_callback(_http_callback,
                                      _http_callback.on_before_request if _http_callback is not None else None,
                                      _http_request, "Calling the on_before_request method of http_call_back for {}.")

            self._endpoint_logger.debug("Raw request for {} is: {}".format(
                self._endpoint_name_for_logging, vars(_http_request)))

            _http_response = _http_client_configuration.http_client.execute(
                _http_request, self._endpoint_configuration)

            self._endpoint_logger.debug("Raw response for {} is: {}".format(
                self._endpoint_name_for_logging, vars(_http_response)))

            self.update_http_callback(_http_callback,
                                      _http_callback.on_after_response if _http_callback is not None else None,
                                      _http_response, "Calling on_after_response method of http_call_back for {}.")

            return self._response_handler.endpoint_logger(self._endpoint_logger) \
                .endpoint_name_for_logging(self._endpoint_name_for_logging) \
                .handle(_http_response, self._global_configuration.get_global_errors())
        except Exception as e:
            self._endpoint_logger.error(e)
            raise

    def update_http_callback(self, http_callback, func, argument, log_message):
        if http_callback is None:
            return

        self._endpoint_logger.info(log_message.format(
            self._endpoint_name_for_logging))
        func(argument)
