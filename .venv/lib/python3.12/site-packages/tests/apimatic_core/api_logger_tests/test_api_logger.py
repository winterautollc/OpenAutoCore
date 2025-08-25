import pytest
from apimatic_core_interfaces.types.http_method_enum import HttpMethodEnum

from apimatic_core.authentication.multiple.single_auth import Single
from apimatic_core.request_builder import RequestBuilder
from apimatic_core.response_handler import ResponseHandler
from apimatic_core.types.parameter import Parameter
from apimatic_core.utilities.api_helper import ApiHelper
from tests.apimatic_core.base import Base
from tests.apimatic_core.mocks.callables.base_uri_callable import Server
from tests.apimatic_core.mocks.logger.api_logger import ApiLogger
from tests.apimatic_core.mocks.models.person import Employee


class TestApiLogger(Base):

    def setup_test(self, global_config):
        self.api_logger = ApiLogger()
        self.global_config = global_config
        self.http_response_catcher = self.global_config.get_http_client_configuration().http_callback
        self.http_client = self.global_config.get_http_client_configuration().http_client
        self.api_call_builder = self.new_api_call_builder(self.global_config, self.api_logger)

    def test_end_to_end_success_case(self):
        self.setup_test(self.global_configuration_with_auth)
        expected_messages = ['Preparing query URL for end-to-end-test.',
                             'Preparing headers for end-to-end-test.',
                             'Preparing body for end-to-end-test.',
                             'Applying auth for end-to-end-test.',
                             'Calling the on_before_request method of http_call_back for end-to-end-test.',
                             'Raw request for end-to-end-test is: {\'http_method\': \'POST\', \'query_url\': '
                             '\'http://localhost:3000/body/model\', \'headers\': {\'Content-Type\': '
                             '\'application/json\', \'accept\': \'application/json\', \'Authorization\': '
                             '\'Basic dGVzdF91c2VybmFtZTp0ZXN0X3Bhc3N3b3Jk\'}, \'query_parameters\': None, '
                             '\'parameters\': \'{"Key": "Value"}\', \'files\': {}}',
                             'Raw response for end-to-end-test is: {\'status_code\': 200, \'reason_phrase\': None, '
                             '\'headers\': {\'Content-Type\': \'application/json\', \'accept\': \'application/json\', '
                             '\'Authorization\': \'Basic dGVzdF91c2VybmFtZTp0ZXN0X3Bhc3N3b3Jk\'}, \'text\': '
                             '\'{"Key": "Value"}\', \'request\': {\'http_method\': \'POST\', \'query_url\': '
                             '\'http://localhost:3000/body/model\', \'headers\': {\'Content-Type\': '
                             '\'application/json\', \'accept\': \'application/json\', \'Authorization\': '
                             '\'Basic dGVzdF91c2VybmFtZTp0ZXN0X3Bhc3N3b3Jk\'}, \'query_parameters\': None, '
                             '\'parameters\': \'{"Key": "Value"}\', \'files\': {}}}',
                             'Calling on_after_response method of http_call_back for end-to-end-test.',
                             'Validating response for end-to-end-test.']
        self.api_call_builder.new_builder.endpoint_name_for_logging("end-to-end-test")\
            .request(RequestBuilder().server(Server.DEFAULT)
                     .path('/body/model')
                     .http_method(HttpMethodEnum.POST)
                     .header_param(Parameter()
                                   .key('Content-Type')
                                   .value('application/json'))
                     .body_param(Parameter()
                                 .value({"Key": "Value"})
                                 .is_required(True))
                     .header_param(Parameter()
                                   .key('accept')
                                   .value('application/json'))
                     .auth(Single('basic_auth'))
                     .body_serializer(ApiHelper.json_serialize)
                     )\
            .response(ResponseHandler()
                      .is_nullify404(True)
                      .deserializer(ApiHelper.json_deserialize)
                      .deserialize_into(Employee.from_dictionary))\
            .execute()

        assert self.api_logger.logged_messages == expected_messages

    def test_end_to_end_with_uninitialized_http_client(self):
        self.setup_test(self.default_global_configuration)
        with pytest.raises(ValueError) as exception:
            self.api_call_builder.new_builder.endpoint_name_for_logging("end-to-end-test") \
                .request(RequestBuilder().server(Server.DEFAULT)
                         .path('/body/model')
                         .http_method(HttpMethodEnum.POST)
                         .header_param(Parameter()
                                       .key('Content-Type')
                                       .value('application/json'))
                         .body_param(Parameter()
                                     .value({"Key": "Value"})
                                     .is_required(True))
                         .header_param(Parameter()
                                       .key('accept')
                                       .value('application/json'))
                         .auth(Single('basic_auth'))
                         .body_serializer(ApiHelper.json_serialize)
                         ) \
                .response(ResponseHandler()
                          .is_nullify404(True)
                          .deserializer(ApiHelper.json_deserialize)
                          .deserialize_into(Employee.from_dictionary)) \
                .execute()
        assert self.api_logger.logged_messages == ['{}-{}'.format(exception.value.args[0], True)]
