from datetime import datetime, date
import jsonpickle
import pytest
from apimatic_core.types.union_types.leaf_type import LeafType
from apimatic_core.types.union_types.one_of import OneOf
from apimatic_core.types.union_types.union_type_context import UnionTypeContext
from dateutil.tz import tzutc

from apimatic_core.types.array_serialization_format import SerializationFormats
from apimatic_core.types.datetime_format import DateTimeFormat
from apimatic_core.types.file_wrapper import FileWrapper
from apimatic_core.utilities.api_helper import ApiHelper
from tests.apimatic_core.base import Base
from tests.apimatic_core.mocks.models.days import Days

from tests.apimatic_core.mocks.models.grand_parent_class_model import ChildClassModel
from tests.apimatic_core.mocks.models.person import Employee
from requests.utils import quote


class TestApiHelper(Base):

    @pytest.mark.parametrize('input_value, expected_value', [
        (None, None),
        (Base.wrapped_parameters(), '{{"bodyScalar": true, "bodyNonScalar": {{"address": "street abc", "age": 27, '
                                    '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
                                    '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
                                    '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
                                    '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
                                    '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
                                    '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
                                    '"Tuesday"], "personType": "Empl"}}}}'.format(
            Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
            Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))),
    ])
    def test_json_serialize_wrapped_params(self, input_value, expected_value):
        request_param = ApiHelper.json_serialize_wrapped_params(input_value)
        assert request_param == expected_value

    @pytest.mark.parametrize('input_value, expected_value', [
        (None, None),
        ([Base.employee_model(), Base.employee_model()],
         '[{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}, '
         '{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}]'.format(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
                                                      Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))),
        ([[Base.employee_model(), Base.employee_model()], [Base.employee_model(), Base.employee_model()]],
         '[[{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}, '
         '{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}], [{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}, '
         '{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}]]'.format(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
                                                      Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))),
        ({'key0': [Base.employee_model(), Base.employee_model()],
          'key1': [Base.employee_model(), Base.employee_model()]},
         '{{"key0": [{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}, '
         '{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}], "key1": [{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}, '
         '{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}]}}'.format(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
                                                      Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))),
        ([1, 2, 3], '[1, 2, 3]'),
        ({'key0': 1, 'key1': 'abc'}, '{"key0": 1, "key1": "abc"}'),
        ([[1, 2, 3], ['abc', 'def']], '[[1, 2, 3], ["abc", "def"]]'),
        ([{'key0': [1, 2, 3]}, {'key1': ['abc', 'def']}], '[{"key0": [1, 2, 3]}, {"key1": ["abc", "def"]}]'),
        ({'key0': [1, 2, 3], 'key1': ['abc', 'def']}, '{"key0": [1, 2, 3], "key1": ["abc", "def"]}'),
        (Base.employee_model(),
         '{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}'.format(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
                                                     Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))),
        (1, '1'),
        ('1', '1')
    ])
    def test_json_serialize(self, input_value, expected_value):
        serialized_value = ApiHelper.json_serialize(input_value)
        assert serialized_value == expected_value

    @pytest.mark.parametrize('input_json_value, unboxing_function, as_dict, expected_value', [
        (None, None, False, None),
        ('true', None, False, 'true'),
        (ApiHelper.json_serialize(Base.employee_model()), Employee.from_dictionary, False,
         ApiHelper.json_serialize(Base.employee_model())),
        (ApiHelper.json_serialize([Base.employee_model(), Base.employee_model()]),
         Employee.from_dictionary, False,
         ApiHelper.json_serialize([Base.employee_model(), Base.employee_model()])),
        (ApiHelper.json_serialize({'key1': Base.employee_model(), 'key2': Base.employee_model()}),
         Employee.from_dictionary, True,
         '{{"key1": {{"address": "street abc", "age": 27, "birthday": "1994-02-13", "birthtime": "{0}", '
         '"department": "IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": "1994-02-13", '
         '"birthtime": "{0}", "name": "John", "uid": 7654321, "personType": "Per", "key1": "value1", '
         '"key2": "value2"}}], "hiredAt": "{1}", "joiningDay": "Monday", "name": "Bob", "salary": 30000, '
         '"uid": 1234567, "workingDays": ["Monday", "Tuesday"], "personType": "Empl"}}, "key2": '
         '{{"address": "street abc", "age": 27, "birthday": "1994-02-13", "birthtime": "{0}", "department": "IT",'
         ' "dependents": [{{"address": "street abc", "age": 12, "birthday": "1994-02-13", "birthtime": "{0}", '
         '"name": "John", "uid": 7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], "hiredAt": "{1}",'
         ' "joiningDay": "Monday", "name": "Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday",'
         ' "Tuesday"], "personType": "Empl"}}}}'.format(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
                                                        Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15))))

    ])
    def test_json_deserialize(self, input_json_value, unboxing_function, as_dict, expected_value):
        deserialized_value = ApiHelper.json_deserialize(input_json_value, unboxing_function, as_dict)
        assert ApiHelper.json_serialize(deserialized_value) == expected_value

    @pytest.mark.parametrize('input_json', [
        True
    ])
    def test_json_deserialize_value_error(self, input_json):
        with pytest.raises(ValueError):
            raise ValueError(input_json)
            ApiHelper.json_deserialize(input_json)

    @pytest.mark.parametrize('input_url, input_file_value, expected_value', [
        ('C:\\PYTHON_GENERIC_LIB\\Tester\\models\\test_file.py', "test_file",
         'C:\\PYTHON_GENERIC_LIB\\Tester\\schemas\\TestFile.json'),
    ])
    def test_get_schema_path(self, input_url, input_file_value, expected_value):
        assert expected_value == ApiHelper.get_schema_path(input_url, input_file_value)

    @pytest.mark.parametrize('input_template_params, expected_template_params', [
        (None, '{template_param}'),
        ({'template_param': {'value': 'Basic Test', 'encode': True}}, 'Basic%20Test'),
        ({'template_param': {'value': 'Basic"Test', 'encode': True}}, 'Basic%22Test'),
        ({'template_param': {'value': 'Basic<Test', 'encode': True}}, 'Basic%3CTest'),
        ({'template_param': {'value': 'Basic>Test', 'encode': True}}, 'Basic%3ETest'),
        ({'template_param': {'value': 'Basic#Test', 'encode': True}}, 'Basic%23Test'),
        ({'template_param': {'value': 'Basic%Test', 'encode': True}}, 'Basic%25Test'),
        ({'template_param': {'value': 'Basic|Test', 'encode': True}}, 'Basic%7CTest'),
        ({'template_param': {'value': 'Basic Test', 'encode': False}}, 'Basic Test'),
        ({'template_param': {'value': 'Basic"Test', 'encode': False}}, 'Basic"Test'),
        ({'template_param': {'value': 'Basic<Test', 'encode': False}}, 'Basic<Test'),
        ({'template_param': {'value': 'Basic>Test', 'encode': False}}, 'Basic>Test'),
        ({'template_param': {'value': 'Basic#Test', 'encode': False}}, 'Basic#Test'),
        ({'template_param': {'value': 'Basic%Test', 'encode': False}}, 'Basic%Test'),
        ({'template_param': {'value': 'Basic|Test', 'encode': False}}, 'Basic|Test'),
        ({'template_param': {'value': None, 'encode': False}}, ''),
    ])
    def test_append_url_with_template_parameters(self, input_template_params, expected_template_params):
        assert ApiHelper.append_url_with_template_parameters('http://localhost:3000/{template_param}',
                                                             input_template_params) \
               == 'http://localhost:3000/{}'.format(expected_template_params)

    @pytest.mark.parametrize('input_template_params', [
        ({'template_param1': {'value': ['Basic Test', 'Basic"Test'], 'encode': True},
          'template_param2': {'value': ['Basic Test', 'Basic"Test'], 'encode': False},
          'template_param3': {'value': 'Basic Test', 'encode': True},
          'template_param4': {'value': 'Basic Test', 'encode': False},
          })])
    def test_append_url_with_template_parameters_multiple_values(self, input_template_params):
        url = 'http://localhost:3000/{template_param1}/{template_param2}/{template_param3}/{template_param4}'
        assert ApiHelper.append_url_with_template_parameters(url, input_template_params) \
               == 'http://localhost:3000/Basic%20Test/Basic%22Test/Basic Test/Basic"Test/Basic%20Test/Basic Test'

    @pytest.mark.parametrize('input_url, input_template_param_value', [
        (None, {'template_param1': {'value': ['Basic Test', 'Basic"Test'], 'encode': True}})
    ])
    def test_append_url_with_template_parameters_value_error(self, input_url, input_template_param_value):
        with pytest.raises(ValueError, match="URL is None."):
            ApiHelper.append_url_with_template_parameters(input_url, input_template_param_value)

    @pytest.mark.parametrize('input_query_param_value, expected_query_param_value, array_serialization_format', [
        (None, '', SerializationFormats.INDEXED),
        ({'query_param': "string"}, 'query_param=string', SerializationFormats.INDEXED),
        ({'query_param': 500}, 'query_param=500', SerializationFormats.INDEXED),
        ({'query_param': 500.12}, 'query_param=500.12', SerializationFormats.INDEXED),
        ({'query_param': date(1994, 2, 13)}, 'query_param=1994-02-13', SerializationFormats.INDEXED),
        ({'query_param': ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15))},
         'query_param=761117415', SerializationFormats.INDEXED),
        ({'query_param': Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15))},
         'query_param={}'.format(quote(Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)), safe='')),
         SerializationFormats.INDEXED),
        ({'query_param': Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15))},
         'query_param={}'.format(quote(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)), safe='')),
         SerializationFormats.INDEXED),
        ({'query_param': [1, 2, 3, 4]}, 'query_param[0]=1&query_param[1]=2&query_param[2]=3&query_param[3]=4',
         SerializationFormats.INDEXED),
        ({'query_param': [1, 2, 3, 4]}, 'query_param[]=1&query_param[]=2&query_param[]=3&query_param[]=4',
         SerializationFormats.UN_INDEXED),
        ({'query_param': [1, 2, 3, 4]}, 'query_param=1&query_param=2&query_param=3&query_param=4',
         SerializationFormats.PLAIN),
        ({'query_param': [1, 2, 3, 4]}, 'query_param=1%2C2%2C3%2C4', SerializationFormats.CSV),
        ({'query_param': [1, 2, 3, 4]}, 'query_param=1%7C2%7C3%7C4', SerializationFormats.PSV),
        ({'query_param': [1, 2, 3, 4]}, 'query_param=1%092%093%094', SerializationFormats.TSV),
        ({'query_param': {'key1': 'value1', 'key2': 'value2'}}, 'query_param[key1]=value1&query_param[key2]=value2',
         SerializationFormats.INDEXED),
        ({'query_param': 1, 'query_param_none': None, 'query_param2': 2}, 'query_param=1&query_param2=2',
         SerializationFormats.INDEXED),
        ({'query_param': {'key1': 'value1', 'key2': [1, 2, 3, 4]}},
         'query_param[key1]=value1'
         '&query_param[key2][0]=1'
         '&query_param[key2][1]=2'
         '&query_param[key2][2]=3'
         '&query_param[key2][3]=4', SerializationFormats.INDEXED),
        ({'query_param': {'key1': 'value1', 'key2': [1, 2, 3, {'key1': 'value1', 'key2': 'value2'}]}},
         'query_param[key1]=value1'
         '&query_param[key2][0]=1'
         '&query_param[key2][1]=2'
         '&query_param[key2][2]=3'
         '&query_param[key2][3][key1]=value1'
         '&query_param[key2][3][key2]=value2', SerializationFormats.INDEXED),
        ({'query_param': Base.employee_model()},
         'query_param[address]=street%20abc'
         '&query_param[age]=27'
         '&query_param[birthday]=1994-02-13'
         '&query_param[birthtime]={}'.format(quote(
             Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)), safe='')) +
         '&query_param[department]=IT'
         '&query_param[dependents][0][address]=street%20abc'
         '&query_param[dependents][0][age]=12'
         '&query_param[dependents][0][birthday]=1994-02-13'
         '&query_param[dependents][0][birthtime]={}'.format(quote(
             Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)), safe='')) +
         '&query_param[dependents][0][name]=John'
         '&query_param[dependents][0][uid]=7654321'
         '&query_param[dependents][0][personType]=Per'
         '&query_param[dependents][0][key1]=value1'
         '&query_param[dependents][0][key2]=value2'
         '&query_param[hiredAt]={}'.format(quote(
             Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)), safe='')) +
         '&query_param[joiningDay]=Monday'
         '&query_param[name]=Bob'
         '&query_param[salary]=30000'
         '&query_param[uid]=1234567'
         '&query_param[workingDays][0]=Monday'
         '&query_param[workingDays][1]=Tuesday'
         '&query_param[personType]=Empl', SerializationFormats.INDEXED)
    ])
    def test_append_url_with_query_parameters(self, input_query_param_value, expected_query_param_value,
                                              array_serialization_format):
        if input_query_param_value is None:
            assert ApiHelper.append_url_with_query_parameters('http://localhost:3000/test', input_query_param_value,
                                                              array_serialization_format) == 'http://localhost:3000/test'
        else:

            assert ApiHelper.append_url_with_query_parameters('http://localhost:3000/test', input_query_param_value,
                                                              array_serialization_format) == \
                   'http://localhost:3000/test?{}'.format(expected_query_param_value)

    @pytest.mark.parametrize('input_url, input_query_param_value', [
        (None, {'query_param': 'string'})
    ])
    def test_append_url_with_query_parameters_value_error(self, input_url, input_query_param_value):
        with pytest.raises(ValueError, match="URL is None."):
            ApiHelper.append_url_with_query_parameters(input_url, input_query_param_value)

    @pytest.mark.parametrize('input_query_params, expected_query_param_value, array_serialization_format', [
        ({'query_param': "string",
          'query_param2': True,
          'query_param3': [1, 2, 3]
          }, 'query_param=string&query_param2=true&query_param3[0]=1&query_param3[1]=2&query_param3[2]=3',
         SerializationFormats.INDEXED)
    ])
    def test_process_complex_query_parameters(self, input_query_params, expected_query_param_value,
                                              array_serialization_format):
        assert ApiHelper.append_url_with_query_parameters('http://localhost:3000/test', input_query_params,
                                                          array_serialization_format) == 'http://localhost:3000/test?{}'.format(
            expected_query_param_value)

    @pytest.mark.parametrize('input_url', [
        'This is not a url'])
    def test_clean_url_value_error(self, input_url):
        with pytest.raises(ValueError, match="Invalid Url format."):
            ApiHelper.clean_url(input_url)

    @pytest.mark.parametrize('input_url, expected_url', [
        ('http://localhost:3000//test', 'http://localhost:3000/test'),
        ('http://localhost:3000//test?'
         'query_param=string&query_param2=True&query_param3[0]=1&query_param3[1]=2query_param3[2]=3',
         'http://localhost:3000/test?'
         'query_param=string&query_param2=True&query_param3[0]=1&query_param3[1]=2query_param3[2]=3',)

    ])
    def test_clean_url(self, input_url, expected_url):
        assert ApiHelper.clean_url(input_url) == expected_url

    @pytest.mark.parametrize('obj, expected_value', [
        (Base.employee_model(),
         '{{"address": "street abc", "age": 27, '
         '"birthday": "1994-02-13", "birthtime": "{0}", "department": '
         '"IT", "dependents": [{{"address": "street abc", "age": 12, "birthday": '
         '"1994-02-13", "birthtime": "{0}", "name": "John", "uid": '
         '7654321, "personType": "Per", "key1": "value1", "key2": "value2"}}], '
         '"hiredAt": "{1}", "joiningDay": "Monday", "name": '
         '"Bob", "salary": 30000, "uid": 1234567, "workingDays": ["Monday", '
         '"Tuesday"], "personType": "Empl"}}'.format(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
                                                     Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))),
        (Base.get_complex_type(),
         '{"innerComplexListType": [{"booleanType": true, "longType": 100003, "precisionType": 55.44, '
         '"stringListType": ["item1", "item2"], "stringType": "abc", "key0": "abc", "key1": 400}, '
         '{"booleanType": true, "longType": 100003, "precisionType": 55.44, "stringListType": ["item1", "item2"],'
         ' "stringType": "abc", "key0": "abc", "key1": 400}], "innerComplexType": {"booleanType": true, '
         '"longType": 100003, "precisionType": 55.44, "stringListType": ["item1", "item2"], "stringType": "abc",'
         ' "key0": "abc", "key1": 400}, "innerComplexListOfMapType": [{"key0": {"booleanType": true, '
         '"longType": 100003, "precisionType": 55.44, "stringListType": ["item1", "item2"], '
         '"stringType": "abc", "key0": "abc", "key1": 400}, "key1": {"booleanType": true, "longType": 100003, '
         '"precisionType": 55.44, "stringListType": ["item1", "item2"], "stringType": "abc", "key0": "abc", '
         '"key1": 400}}], "innerComplexMapOfListType": {"key0": [{"booleanType": true, "longType": 100003, '
         '"precisionType": 55.44, "stringListType": ["item1", "item2"], "stringType": "abc", "key0": "abc", '
         '"key1": 400}, {"booleanType": true, "longType": 100003, "precisionType": 55.44, "stringListType": '
         '["item1", "item2"], "stringType": "abc", "key0": "abc", "key1": 400}], "key2": [{"booleanType": true, '
         '"longType": 100003, "precisionType": 55.44, "stringListType": ["item1", "item2"], "stringType": "abc", '
         '"key0": "abc", "key1": 400}, {"booleanType": true, "longType": 100003, "precisionType": 55.44, '
         '"stringListType": ["item1", "item2"], "stringType": "abc", "key0": "abc", "key1": 400}]}, '
         '"innerComplexMapType": {"key0": {"booleanType": true, "longType": 100003, "precisionType": 55.44, '
         '"stringListType": ["item1", "item2"], "stringType": "abc", "key0": "abc", "key1": 400}, "key1": '
         '{"booleanType": true, "longType": 100003, "precisionType": 55.44, "stringListType": ["item1", "item2"], '
         '"stringType": "abc", "key0": "abc", "key1": 400}}, "prop1": [1, 2, 3], "prop2": {"key0": "abc", '
         '"key1": "def"}}'),
        (ApiHelper.json_deserialize('{"Grand_Parent_Required_Nullable":{"key1": "value1", "key2": "value2"},'
                                    '"Grand_Parent_Required":"not nullable and required","class":23,'
                                    '"Parent_Optional_Nullable_With '
                                    '_Default_Value":"Has default value","Parent_Required_Nullable":nul'
                                    'l,"Parent_Required":"not nullable and required","Optional_Nullable'
                                    '":"setted optionalNullable","Optional_Nullable_With_Default_Value"'
                                    ':"With default value","Required_Nullable":null,"Required":"not nul'
                                    'lable and required","Optional":"not nullable and optional","Child_'
                                    'Class_Array":null}', ChildClassModel.from_dictionary),
         '{"Required_Nullable": null, "Required": "not nullable and required", '
         '"Parent_Required_Nullable": null, "Parent_Required": "not nullable and '
         'required", "Grand_Parent_Required_Nullable": {"key1": "value1", "key2": '
         '"value2"}, "Grand_Parent_Required": "not nullable and required", '
         '"Optional_Nullable": "setted optionalNullable", '
         '"Optional_Nullable_With_Default_Value": "With default value", "Optional": '
         '"not nullable and optional", "Child_Class_Array": null, "class": 23, '
         '"Parent_Optional_Nullable_With_Default_Value": "Has default value"}'
         ),
        (Base.employee_model_additional_dictionary(),
         '{{"address": "street abc", "age": 27, "birthday": "1994-02-13", "birthtime": '
         '"{0}", "department": "IT", "dependents": [{{"address": '
         '"street abc", "age": 12, "birthday": "1994-02-13", "birthtime": '
         '"{0}", "name": "John", "uid": 7654321, "personType": "Per", '
         '"key1": {{"inner_key1": "inner_val1", "inner_key2": "inner_val2"}}, "key2": '
         '["value2", "value3"]}}], "hiredAt": "{1}", '
         '"joiningDay": "Monday", "name": "Bob", "salary": 30000, "uid": 1234567, '
         '"workingDays": ["Monday", "Tuesday"], "personType": "Empl"}}'.format(
             Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
             Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))),
        (Base.get_union_type_scalar_model(),
         '{"anyOfRequired": 1.5, "oneOfReqNullable": "abc", "oneOfOptional": 200, "anyOfOptNullable": true}'),

    ])
    def test_to_dictionary(self, obj, expected_value):
        assert jsonpickle.encode(ApiHelper.to_dictionary(obj), False) == expected_value

    @pytest.mark.parametrize('obj, should_ignore_null_values, expected_value', [
        (Base.employee_model_additional_dictionary(), True,
         '{{"address": "street abc", "age": 27, "birthday": "1994-02-13", "birthtime": '
         '"{0}", "department": "IT", "dependents": [{{"address": '
         '"street abc", "age": 12, "birthday": "1994-02-13", "birthtime": '
         '"{0}", "name": "John", "uid": 7654321, "personType": "Per", '
         '"key1": {{"inner_key1": "inner_val1", "inner_key2": "inner_val2"}}, "key2": '
         '["value2", "value3"]}}], "hiredAt": "{1}", '
         '"joiningDay": "Monday", "name": "Bob", "salary": 30000, "uid": 1234567, '
         '"workingDays": ["Monday", "Tuesday"], "personType": "Empl"}}'.format(
             Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
             Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))),
        (ApiHelper.json_deserialize('{"Grand_Parent_Required_Nullable":{"key1": "value1", "key2": "value2"},'
                                    '"Grand_Parent_Required":"not nullable and required","class":23,'
                                    '"Parent_Optional_Nullable_With '
                                    '_Default_Value":"Has default value","Parent_Required_Nullable":nul'
                                    'l,"Parent_Required":"not nullable and required","Optional_Nullable'
                                    '":"setted optionalNullable","Optional_Nullable_With_Default_Value"'
                                    ':"With default value","Required_Nullable":null,"Required":"not nul'
                                    'lable and required","Optional":"not nullable and optional","Child_'
                                    'Class_Array":null}', ChildClassModel.from_dictionary), True,
         '{"Required_Nullable": null, "Required": "not nullable and required", '
         '"Parent_Required_Nullable": null, "Parent_Required": "not nullable and '
         'required", "Grand_Parent_Required_Nullable": {"key1": "value1", "key2": '
         '"value2"}, "Grand_Parent_Required": "not nullable and required", '
         '"Optional_Nullable": "setted optionalNullable", '
         '"Optional_Nullable_With_Default_Value": "With default value", "Optional": '
         '"not nullable and optional", "Child_Class_Array": null, "class": 23, '
         '"Parent_Optional_Nullable_With_Default_Value": "Has default value"}'
         ),
    ])
    def test_to_dictionary_for_object(self, obj, should_ignore_null_values, expected_value):
        assert jsonpickle.encode(ApiHelper.to_dictionary(obj), False) == expected_value

    @pytest.mark.parametrize('obj, name', [
        (ApiHelper.json_deserialize('{"Grand_Parent_Required_Nullable":{"key1": "value1", "key2": "value2"},'
                                    '"Grand_Parent_Required":"not nullable and required","class":23,'
                                    '"Parent_Optional_Nullable_With '
                                    '_Default_Value":"Has default value","Parent_Required_Nullable":nul'
                                    'l,"Parent_Required":"not nullable and required","Optional_Nullable'
                                    '":"setted optionalNullable","Optional_Nullable_With_Default_Value"'
                                    ':"With default value","Required_Nullable":null,"Optional":"not nullable and '
                                    'optional","Child_Class_Array":null}', ChildClassModel.from_dictionary),
         'required'),
    ])
    def test_to_dictionary_value_error(self, obj, name):
        with pytest.raises(ValueError, match=f"The value for {name} can not be None for {obj}"):
            ApiHelper.to_dictionary(obj)

    @pytest.mark.parametrize('input_form_param_value, expected_form_param_value, array_serialization_format', [
        (None, [], SerializationFormats.INDEXED),
        ('string', [('form_param', 'string')], SerializationFormats.INDEXED),
        (500, [('form_param', 500)], SerializationFormats.INDEXED),
        (500.12, [('form_param', 500.12)], SerializationFormats.INDEXED),
        (str(date(1994, 2, 13)), [('form_param', '1994-02-13')], SerializationFormats.INDEXED),
        (ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         [('form_param', 761117415)], SerializationFormats.INDEXED),
        (Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         [('form_param', Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)))], SerializationFormats.INDEXED),
        (Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         [('form_param', Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)))], SerializationFormats.INDEXED),
        ([1, 2, 3, 4], [('form_param[0]', 1), ('form_param[1]', 2), ('form_param[2]', 3), ('form_param[3]', 4)],
         SerializationFormats.INDEXED),
        ([1, 2, 3, 4], [('form_param[]', 1), ('form_param[]', 2), ('form_param[]', 3), ('form_param[]', 4)],
         SerializationFormats.UN_INDEXED),
        ([1, 2, 3, 4], [('form_param', 1), ('form_param', 2), ('form_param', 3), ('form_param', 4)],
         SerializationFormats.PLAIN),
        ({'key1': 'value1', 'key2': 'value2'}, [('form_param[key1]', 'value1'), ('form_param[key2]', 'value2')],
         SerializationFormats.INDEXED),
        ({'key1': 'value1', 'key2': [1, 2, 3, 4]},
         [('form_param[key1]', 'value1'), ('form_param[key2][0]', 1), ('form_param[key2][1]', 2),
          ('form_param[key2][2]', 3), ('form_param[key2][3]', 4)], SerializationFormats.INDEXED),
        ({'key1': 'value1', 'key2': [1, 2, 3, {'key1': 'value1', 'key2': 'value2'}]},
         [('form_param[key1]', 'value1'), ('form_param[key2][0]', 1), ('form_param[key2][1]', 2),
          ('form_param[key2][2]', 3), ('form_param[key2][3][key1]', 'value1'), ('form_param[key2][3][key2]', 'value2')],
         SerializationFormats.INDEXED),
        (Base.employee_model(),
         [('form_param[address]', 'street abc'), ('form_param[age]', 27), ('form_param[birthday]', '1994-02-13'),
          ('form_param[birthtime]', Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15), False)),
          ('form_param[department]', 'IT'), ('form_param[dependents][0][address]', 'street abc'),
          ('form_param[dependents][0][age]', 12), ('form_param[dependents][0][birthday]', '1994-02-13'),
          ('form_param[dependents][0][birthtime]', Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15), False)),
          ('form_param[dependents][0][name]', 'John'), ('form_param[dependents][0][uid]', 7654321),
          ('form_param[dependents][0][personType]', 'Per'), ('form_param[dependents][0][key1]', 'value1'),
          ('form_param[dependents][0][key2]', 'value2'),
          ('form_param[hiredAt]', Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15), False)),
          ('form_param[joiningDay]', 'Monday'), ('form_param[name]', 'Bob'), ('form_param[salary]', 30000),
          ('form_param[uid]', 1234567), ('form_param[workingDays][0]', 'Monday'),
          ('form_param[workingDays][1]', 'Tuesday'), ('form_param[personType]', 'Empl')], SerializationFormats.INDEXED)
    ])
    def test_form_params(self, input_form_param_value, expected_form_param_value, array_serialization_format):
        key = 'form_param'
        form_encoded_params = ApiHelper.form_encode(input_form_param_value, key, array_serialization_format)
        for index, item in enumerate(form_encoded_params):
            # form encoding stores the datetime object so converting datetime to string for assertions as assertions
            # do not work for objects
            if isinstance(item[1], ApiHelper.CustomDate):
                assert item[0] == expected_form_param_value[index][0] \
                       and item[1].value == expected_form_param_value[index][1].value
            else:
                assert item == expected_form_param_value[index]

    @pytest.mark.parametrize('input_form_param_value, expected_form_param_value, array_serialization_format', [
        ({'form_param1': 'string',
          'form_param2': ['string', True],
          'form_param3': {'key': 'string_val'},
          }, [('form_param1', 'string'),
              ('form_param2[0]', 'string'),
              ('form_param2[1]', 'true'),
              ('form_param3[key]', 'string_val')], SerializationFormats.INDEXED)
    ])
    def test_form_encode_parameters(self, input_form_param_value, expected_form_param_value,
                                    array_serialization_format):
        assert ApiHelper.form_encode_parameters(input_form_param_value, array_serialization_format) == \
               expected_form_param_value

    @pytest.mark.parametrize('input_function, input_body, expected_value', [
        (ApiHelper.RFC3339DateTime, ApiHelper.RFC3339DateTime.from_value('1994-02-13T14:01:54.9571247Z').datetime,
         '1994-02-13T14:01:54.957124+00:00'),
        (ApiHelper.RFC3339DateTime, None, None)
    ])
    def test_when_defined(self, input_function, input_body, expected_value):
        if input_body is not None:
            assert str(ApiHelper.when_defined(input_function, input_body)) == expected_value
        else:
            assert ApiHelper.when_defined(input_function, input_body) == expected_value

    @pytest.mark.parametrize('input_value, input_converter, expected_obj', [
        (datetime(1994, 2, 13, 5, 30, 15), ApiHelper.RFC3339DateTime,
         ApiHelper.RFC3339DateTime),
        (datetime(1994, 2, 13, 5, 30, 15), ApiHelper.HttpDateTime, ApiHelper.HttpDateTime),
        (datetime(1994, 2, 13, 5, 30, 15), ApiHelper.UnixDateTime, ApiHelper.UnixDateTime),
        (500, ApiHelper.UnixDateTime, int),
        ('500', ApiHelper.UnixDateTime, str),
        (None, ApiHelper.RFC3339DateTime, None)
    ])
    def test_apply_date_time_converter(self, input_value, input_converter, expected_obj):
        if input_value is None:
            assert ApiHelper.apply_datetime_converter(input_value, input_converter) == expected_obj
        else:
            assert isinstance(ApiHelper.apply_datetime_converter(input_value, input_converter), expected_obj)

    @pytest.mark.parametrize('input_value, input_converter, expected_obj', [
        ([datetime(1994, 2, 13, 5, 30, 15), datetime(1994, 2, 13, 5, 30, 15)], ApiHelper.RFC3339DateTime,
         [ApiHelper.RFC3339DateTime, ApiHelper.RFC3339DateTime]),
        ([datetime(1994, 2, 13, 5, 30, 15), datetime(1994, 2, 13, 5, 30, 15)], ApiHelper.HttpDateTime,
         [ApiHelper.HttpDateTime, ApiHelper.HttpDateTime]),
        ([datetime(1994, 2, 13, 5, 30, 15), datetime(1994, 2, 13, 5, 30, 15)], ApiHelper.UnixDateTime,
         [ApiHelper.UnixDateTime, ApiHelper.UnixDateTime]),
        ([500, 1000], ApiHelper.UnixDateTime, [int, int]),
        (['500', '1000'], ApiHelper.UnixDateTime, [str, str]),
        (['500', datetime(1994, 2, 13, 5, 30, 15)], ApiHelper.UnixDateTime, [str, ApiHelper.UnixDateTime]),
        (None, ApiHelper.RFC3339DateTime, None)
    ])
    def test_apply_date_time_converter_to_list(self, input_value, input_converter, expected_obj):
        if input_value is None:
            assert ApiHelper.apply_datetime_converter(input_value, input_converter) == expected_obj
        else:
            actual_converted_value = ApiHelper.apply_datetime_converter(input_value, input_converter)
            for index, actual_value in enumerate(actual_converted_value):
                assert isinstance(actual_value, expected_obj[index])

    @pytest.mark.parametrize('input_value, input_converter, expected_obj', [
        ([[datetime(1994, 2, 13, 5, 30, 15), datetime(1994, 2, 13, 5, 30, 15)]], ApiHelper.RFC3339DateTime,
         [[ApiHelper.RFC3339DateTime, ApiHelper.RFC3339DateTime]]),
        ([[datetime(1994, 2, 13, 5, 30, 15), datetime(1994, 2, 13, 5, 30, 15)]], ApiHelper.HttpDateTime,
         [[ApiHelper.HttpDateTime, ApiHelper.HttpDateTime]]),
        ([[datetime(1994, 2, 13, 5, 30, 15), datetime(1994, 2, 13, 5, 30, 15)]], ApiHelper.UnixDateTime,
         [[ApiHelper.UnixDateTime, ApiHelper.UnixDateTime]]),
        ([[500, 1000]], ApiHelper.UnixDateTime, [[int, int]]),
        ([['500', '1000']], ApiHelper.UnixDateTime, [[str, str]]),
        ([['500', datetime(1994, 2, 13, 5, 30, 15)]], ApiHelper.UnixDateTime, [[str, ApiHelper.UnixDateTime]]),
        (None, ApiHelper.RFC3339DateTime, None)
    ])
    def test_apply_date_time_converter_to_list_of_list(self, input_value, input_converter, expected_obj):
        if input_value is None:
            assert ApiHelper.apply_datetime_converter(input_value, input_converter) == expected_obj
        else:
            actual_converted_value = ApiHelper.apply_datetime_converter(input_value, input_converter)
            for outer_index, actual_outer_value in enumerate(actual_converted_value):
                for index, actual_value in enumerate(actual_outer_value):
                    assert isinstance(actual_value, expected_obj[outer_index][index])

    @pytest.mark.parametrize('input_value, input_converter, expected_obj', [
        ({'key0': datetime(1994, 2, 13, 5, 30, 15), 'key1': datetime(1994, 2, 13, 5, 30, 15)}, ApiHelper.RFC3339DateTime,
         [ApiHelper.RFC3339DateTime, ApiHelper.RFC3339DateTime]),
        ({'key0': datetime(1994, 2, 13, 5, 30, 15), 'key1': datetime(1994, 2, 13, 5, 30, 15)}, ApiHelper.HttpDateTime,
         [ApiHelper.HttpDateTime, ApiHelper.HttpDateTime]),
        ({'key0': datetime(1994, 2, 13, 5, 30, 15), 'key1': datetime(1994, 2, 13, 5, 30, 15)}, ApiHelper.UnixDateTime,
         [ApiHelper.UnixDateTime, ApiHelper.UnixDateTime]),
        ({'key0': '5000', 'key1': datetime(1994, 2, 13, 5, 30, 15)}, ApiHelper.UnixDateTime,
         [str, ApiHelper.UnixDateTime]),
        ({'key0': 5000, 'key1': 10000}, ApiHelper.UnixDateTime, [int, int]),
        ({'key0': '5000', 'key1': '10000'}, ApiHelper.UnixDateTime, [str, str]),
        (None, ApiHelper.RFC3339DateTime, None)
    ])
    def test_apply_date_time_converter_to_dict(self, input_value, input_converter, expected_obj):
        if input_value is None:
            assert ApiHelper.apply_datetime_converter(input_value, input_converter) == expected_obj
        else:
            actual_converted_value = ApiHelper.apply_datetime_converter(input_value, input_converter)
            for index, actual_value in enumerate(actual_converted_value.values()):
                assert isinstance(actual_value, expected_obj[index])

    @pytest.mark.parametrize('input_value, input_converter, expected_obj', [
        ({'key': {'key0': datetime(1994, 2, 13, 5, 30, 15), 'key1': datetime(1994, 2, 13, 5, 30, 15)}},
         ApiHelper.RFC3339DateTime, {'key': [ApiHelper.RFC3339DateTime, ApiHelper.RFC3339DateTime]}),
        ({'key': {'key0': datetime(1994, 2, 13, 5, 30, 15), 'key1': datetime(1994, 2, 13, 5, 30, 15)}}, ApiHelper.HttpDateTime,
         {'key': [ApiHelper.HttpDateTime, ApiHelper.HttpDateTime]}),
        ({'key': {'key0': datetime(1994, 2, 13, 5, 30, 15), 'key1': datetime(1994, 2, 13, 5, 30, 15)}}, ApiHelper.UnixDateTime,
         {'key': [ApiHelper.UnixDateTime, ApiHelper.UnixDateTime]}),
        ({'key': {'key0': '5000', 'key1': datetime(1994, 2, 13, 5, 30, 15)}}, ApiHelper.UnixDateTime,
         {'key': [str, ApiHelper.UnixDateTime]}),
        ({'key': {'key0': 5000, 'key1': 10000}}, ApiHelper.UnixDateTime, {'key': [int, int]}),
        ({'key': {'key0': '5000', 'key1': '10000'}}, ApiHelper.UnixDateTime, {'key': [str, str]}),
        (None, ApiHelper.RFC3339DateTime, None)
    ])
    def test_apply_date_time_converter_to_dict_of_dict(self, input_value, input_converter, expected_obj):
        if input_value is None:
            assert ApiHelper.apply_datetime_converter(input_value, input_converter) == expected_obj
        else:
            actual_converted_value = ApiHelper.apply_datetime_converter(input_value, input_converter)
            for outer_key, actual_outer_value in actual_converted_value.items():
                for index, actual_value in enumerate(actual_outer_value.values()):
                    assert isinstance(actual_value, expected_obj[outer_key][index])

    @pytest.mark.parametrize('input_array,formatting, is_query, expected_array', [
        ([1, True, 'string', 2.36, Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
          str(date(1994, 2, 13))], SerializationFormats.INDEXED, False, [('test_array[0]', 1),
                                                                         ('test_array[1]', True),
                                                                         ('test_array[2]', 'string'),
                                                                         ('test_array[3]', 2.36),
                                                                         ('test_array[4]', Base.get_rfc3339_datetime(
                                                                             datetime(1994, 2, 13, 5, 30, 15))),
                                                                         ('test_array[5]', '1994-02-13')]),
        ([1, True, 'string', 2.36, Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
          str(date(1994, 2, 13))], SerializationFormats.UN_INDEXED, False, [('test_array[]', 1),
                                                                            ('test_array[]', True),
                                                                            ('test_array[]', 'string'),
                                                                            ('test_array[]', 2.36),
                                                                            ('test_array[]', Base.get_rfc3339_datetime(
                                                                                datetime(1994, 2, 13, 5, 30, 15))),
                                                                            ('test_array[]', '1994-02-13')]),
        ([1, True, 'string', 2.36, Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
          str(date(1994, 2, 13))], SerializationFormats.PLAIN, False, [('test_array', 1),
                                                                       ('test_array', True),
                                                                       ('test_array', 'string'),
                                                                       ('test_array', 2.36),
                                                                       ('test_array', Base.get_rfc3339_datetime(
                                                                           datetime(1994, 2, 13, 5, 30, 15))),
                                                                       ('test_array', '1994-02-13')]),
        ([1, True, 'string', 2.36, Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
          str(date(1994, 2, 13))], SerializationFormats.CSV, True,
         [('test_array',
           '1,True,string,2.36,{0},1994-02-13'.format(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15))))]),
        ([1, True, 'string', 2.36, Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
          str(date(1994, 2, 13))], SerializationFormats.PSV, True,
         [('test_array',
           '1|True|string|2.36|{0}|1994-02-13'.format(Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15))))]),
        ([1, True, 'string', 2.36, Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
          str(date(1994, 2, 13))], SerializationFormats.TSV, True,
         [('test_array', '1\tTrue\tstring\t2.36\t{0}\t1994-02-13'.format(
             Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15))))]),
        ([Base.employee_model(), Base.employee_model()], SerializationFormats.INDEXED, False,
         [ApiHelper.json_serialize(Base.employee_model()), ApiHelper.json_serialize(Base.employee_model())]),

    ])
    def test_serialize_array(self, input_array, formatting, is_query, expected_array):
        serialized_array = ApiHelper.serialize_array('test_array', input_array, formatting, is_query)
        if hasattr(input_array[0], '_names'):
            assert serialized_array[0][0] == 'test_array[0]' and serialized_array[1][0] == 'test_array[1]' and \
                   ApiHelper.json_serialize(serialized_array[0][1]) == expected_array[0] \
                   and ApiHelper.json_serialize(serialized_array[1][1]) == expected_array[1]
        else:
            assert ApiHelper.serialize_array('test_array', input_array, formatting, is_query) == expected_array

    @pytest.mark.parametrize('input_array,formatting, is_query', [
        ([1, True, 'string', 2.36, Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
          str(date(1994, 2, 13))], SerializationFormats.TSV, False),
        ([1, True, 'string', 2.36, Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15)),
          str(date(1994, 2, 13))], 'not a serialization format', True)
    ])
    def test_serialize_array_value_error(self, input_array, formatting, is_query):
        with pytest.raises(ValueError, match="Invalid format provided."):
            ApiHelper.serialize_array('key', input_array, formatting, is_query)

    @pytest.mark.parametrize('input_date, expected_date', [
        (str(date(1994, 2, 13)), date(1994, 2, 13)),
        (ApiHelper.json_serialize([str(date(1994, 2, 13)), str(date(1994, 2, 13))]),
         [date(1994, 2, 13), date(1994, 2, 13)])
    ])
    def test_date_deserialize(self, input_date, expected_date):
        assert ApiHelper.date_deserialize(input_date) == expected_date

    @pytest.mark.parametrize('input_http_response, input_date_time_format, expected_response_body', [
        (None, None, None),
        (ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         DateTimeFormat.UNIX_DATE_TIME, datetime(1994, 2, 13, 5, 30, 15)),
        (ApiHelper.HttpDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         DateTimeFormat.HTTP_DATE_TIME, datetime(1994, 2, 13, 5, 30, 15)),
        (ApiHelper.RFC3339DateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         DateTimeFormat.RFC3339_DATE_TIME, datetime(1994, 2, 13, 5, 30, 15)),
        (ApiHelper.json_serialize([ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
                                   ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15))]),
         DateTimeFormat.UNIX_DATE_TIME, [datetime(1994, 2, 13, 5, 30, 15), datetime(1994, 2, 13, 5, 30, 15)]),
        (ApiHelper.json_serialize([ApiHelper.HttpDateTime.from_datetime(datetime(1995, 2, 13, 5, 30, 15)),
                                   ApiHelper.HttpDateTime.from_datetime(datetime(1995, 2, 13, 5, 30, 15))]),
         DateTimeFormat.HTTP_DATE_TIME, [datetime(1995, 2, 13, 5, 30, 15), datetime(1995, 2, 13, 5, 30, 15)]),
        (ApiHelper.json_serialize([ApiHelper.RFC3339DateTime.from_datetime(datetime(1996, 2, 13, 5, 30, 15)),
                                   ApiHelper.RFC3339DateTime.from_datetime(datetime(1996, 2, 13, 5, 30, 15))]),
         DateTimeFormat.RFC3339_DATE_TIME, [datetime(1996, 2, 13, 5, 30, 15), datetime(1996, 2, 13, 5, 30, 15)])

    ])
    def test_date_time_response_body(self, input_http_response, input_date_time_format, expected_response_body):
        assert ApiHelper.datetime_deserialize(input_http_response, input_date_time_format) == expected_response_body

    @pytest.mark.parametrize('input_file_wrapper, is_file_instance', [
        (FileWrapper(Base.read_file('apimatic.png'), 'image/png'), True),
        ('I am not a file', False)
    ])
    def test_is_file_wrapper_instance(self, input_file_wrapper, is_file_instance):
        assert ApiHelper.is_file_wrapper_instance(input_file_wrapper) == is_file_instance

    @pytest.mark.parametrize(' input_date, output_date', [
        (datetime(1994, 2, 13, 5, 30, 15), Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15))),
    ])
    def test_http_datetime_from_datetime(self, input_date, output_date):
        assert ApiHelper.HttpDateTime.from_datetime(input_date) == output_date

    @pytest.mark.parametrize('input_date, output_date', [
        (datetime(1994, 2, 13, 5, 30, 15), Base.get_rfc3339_datetime(datetime(1994, 2, 13, 5, 30, 15))),
    ])
    def test_rfc3339_datetime_from_datetime(self, input_date, output_date):
        assert ApiHelper.RFC3339DateTime.from_datetime(input_date) == output_date

    @pytest.mark.parametrize('input_date, output_date', [
        (datetime(1994, 2, 13, 5, 30, 15), 761117415),
    ])
    def test_unix_datetime_from_datetime(self, input_date, output_date):
        assert ApiHelper.UnixDateTime.from_datetime(input_date) == output_date

    @pytest.mark.parametrize('input_date, output_date', [
        (Base.get_http_datetime(datetime(1994, 2, 13, 5, 30, 15)), datetime(1994, 2, 13, 5, 30, 15)),
    ])
    def test_http_datetime_from_value(self, input_date, output_date):
        assert ApiHelper.HttpDateTime.from_value(input_date).datetime == output_date

    @pytest.mark.parametrize('input_date, output_date', [
        ('1994-02-13T14:01:54.9571247Z', datetime(1994, 2, 13, 14, 1, 54, 957124, tzinfo=tzutc())),
    ])
    def test_rfc3339_from_value(self, input_date, output_date):
        assert ApiHelper.RFC3339DateTime.from_value(input_date).datetime == output_date

    @pytest.mark.parametrize('input_date, output_date', [
        (1484719381, datetime(2017, 1, 18, 6, 3, 1)),
    ])
    def test_unix_datetime_from_value(self, input_date, output_date):
        assert ApiHelper.UnixDateTime.from_value(input_date).datetime == output_date

    @pytest.mark.parametrize('input_value, output_value', [
        (None, None),
        (1, 'text/plain; charset=utf-8'),
        (1.4, 'text/plain; charset=utf-8'),
        (True, 'text/plain; charset=utf-8'),
        ('string', 'text/plain; charset=utf-8'),
        (Base.employee_model(), 'application/json; charset=utf-8'),
    ])
    def test_get_content_type(self, input_value, output_value):
        assert ApiHelper.get_content_type(input_value) == output_value

    @pytest.mark.parametrize('input_value, output_value', [
        ('{"method": "GET", "body": {}, "uploadCount": 0}', {'body': {}, 'method': 'GET', 'uploadCount': 0}),
        ('I am a string', 'I am a string'),
        (None, None)
    ])
    def test_dynamic_deserialize(self, input_value, output_value):
        assert ApiHelper.dynamic_deserialize(input_value) == output_value

    @pytest.mark.parametrize('input_placeholders, input_values, input_template, expected_message', [
        ({}, '400', 'Test template -- {$statusCode}', 'Test template -- {$statusCode}'),
        ({'{$statusCode}'}, '400', 'Test template -- {$statusCode}', 'Test template -- 400'),
        ({'{$response.header.accept}'}, {'accept': 'application/json'},
         'Test template -- {$response.header.accept}', 'Test template -- application/json'),
        ({'{$response.header.accept}'}, {'retry-after': 60},
         'Test template -- {$response.header.accept}', 'Test template -- '),
        ({'{accept}'}, {'accept': 'application/json'},
         'Test template -- {accept}', 'Test template -- application/json')
    ])
    def test_resolve_template_placeholders(self, input_placeholders, input_values, input_template, expected_message):
        actual_message = ApiHelper.resolve_template_placeholders(input_placeholders, input_values, input_template)
        assert actual_message == expected_message

    @pytest.mark.parametrize('input_placeholders, input_value, input_template, expected_message', [
        ({},
         {"scalar": 123.2,
          "object": {"keyA": {"keyC": True, "keyD": 34}, "keyB": "some string", "arrayScalar": ["value1", "value2"],
                     "arrayObjects":[{"key1": 123, "key2": False}, {"key3": 1234, "key4": None}]}},
         'Test template -- {$response.body#/scalar}, {$response.body#/object/arrayObjects/0/key2}',
         'Test template -- {$response.body#/scalar}, {$response.body#/object/arrayObjects/0/key2}'),
        ({'{$response.body#/scalar}', '{$response.body#/object/arrayObjects/0/key2}'},
         {"scalar": 123.2,
          "object": {"keyA": {"keyC": True, "keyD": 34}, "keyB": "some string", "arrayScalar": ["value1", "value2"],
                     "arrayObjects":[{"key1": 123, "key2": False}, {"key3": 1234, "key4": None}]}},
         'Test template -- {$response.body#/scalar}, {$response.body#/object/arrayObjects/0/key2}',
         'Test template -- 123.2, False'),
        ({'{$response.body#/scalar}', '{$response.body#/object/arrayObjects/0/key2}'},
         {"object": {"keyA": {"keyC": True, "keyD": 34}, "keyB": "some string", "arrayScalar": ["value1", "value2"],
                     "arrayObjects": [{"key1": 123, "key2": False}, {"key3": 1234, "key4": None}]}},
         'Test template -- {$response.body#/scalar}, {$response.body#/object/arrayObjects/0/key2}',
         'Test template -- , False'),
        ({'{$response.body}'},
         {"scalar": 123.2,
          "object": {"keyA": {"keyC": True, "keyD": 34}, "keyB": "some string", "arrayScalar": ["value1", "value2"],
                     "arrayObjects": [{"key1": 123, "key2": False}, {"key3": 1234, "key4": None}]}},
         'Test template -- {$response.body}',
         'Test template -- {"scalar": 123.2, "object": {"keyA": {"keyC": true, "keyD": 34}, "keyB": "some string", '
         '"arrayScalar": ["value1", "value2"], '
         '"arrayObjects": [{"key1": 123, "key2": false}, {"key3": 1234, "key4": null}]}}'),
        ({'{$response.body#/object}'},
         {"scalar": 123.2,
          "object": {"keyA": {"keyC": True, "keyD": 34}, "keyB": "some string", "arrayScalar": ["value1", "value2"],
                     "arrayObjects": [{"key1": 123, "key2": False}, {"key3": 1234, "key4": None}]}},
         'Test template -- {$response.body#/object}',
         'Test template -- {"keyA": {"keyC": true, "keyD": 34}, "keyB": "some string", "arrayScalar": '
         '["value1", "value2"], "arrayObjects": [{"key1": 123, "key2": false}, {"key3": 1234, "key4": null}]}'),
        ({'{$response.body}'},
         None,
         'Test template -- {$response.body}',
         'Test template -- ')
    ])
    def test_resolve_template_placeholders_using_json_pointer(self, input_placeholders, input_value, input_template,
                                                              expected_message):
        actual_message = ApiHelper.resolve_template_placeholders_using_json_pointer(input_placeholders, input_value,
                                                                                    input_template)
        assert actual_message == expected_message

    @pytest.mark.parametrize('input_value, input_callable, expected_value', [
        (100, lambda value: isinstance(value, int), True),
        ('100', lambda value: isinstance(value, str), True),
        ("Sunday", lambda value: Days.validate(value), True),
        (100.5, lambda value: isinstance(value, str), False),
        ("Invalid", lambda value: Days.validate(value), False),
        (None, lambda value: isinstance(value, str), False),
        (None, None, False),

        ([100, 200], lambda value: isinstance(value, int), True),
        (['100', '200'], lambda value: isinstance(value, str), True),
        (["Sunday", "Monday"], lambda value: Days.validate(value), True),
        ([100.5, 200], lambda value: isinstance(value, str), False),
        (["Invalid1", "Invalid2"], lambda value: Days.validate(value), False),
        ([None, None], lambda value: isinstance(value, str), False),

        ([[100, 200], [300, 400]], lambda value: isinstance(value, int), True),
        ([['100', '200'], ['abc', 'def']], lambda value: isinstance(value, str), True),
        ([["Sunday", "Monday"], ["Tuesday", "Friday"]], lambda value: Days.validate(value), True),
        ([[100.5, 200], [400, 500]], lambda value: isinstance(value, str), False),
        ([["Invalid1", "Invalid2"], ["Sunday", "Invalid4"]], lambda value: Days.validate(value), False),
        ([[None, None], [None, None]], lambda value: isinstance(value, str), False),

        ({'key0': 100, 'key2': 200}, lambda value: isinstance(value, int), True),
        ({'key0': 'abc', 'key2': 'def'}, lambda value: isinstance(value, str), True),
        ({'key0': 'Sunday', 'key2': 'Tuesday'}, lambda value: Days.validate(value), True),
        ({'key0': 100.5, 'key2': 200}, lambda value: isinstance(value, str), False),
        ({'key0': "Invalid1", 'key2': "Invalid2"}, lambda value: Days.validate(value), False),
        ({'key0': None, 'key2': None}, lambda value: isinstance(value, str), False),
    ])
    def test_is_valid_type(self, input_value, input_callable, expected_value):
        actual_value = ApiHelper.is_valid_type(input_value, input_callable)
        assert actual_value == expected_value

    @pytest.mark.parametrize('input_value, input_union_type, input_should_deserialize, expected_value', [
        (100, OneOf([LeafType(int), LeafType(str)]), False, 100),
        ('[100, "200"]', OneOf([LeafType(int), LeafType(str)], UnionTypeContext.create(is_array=True)), True,
         [100, '200']),
    ])
    def test_union_type_deserialize(self, input_value, input_union_type, input_should_deserialize, expected_value):
        actual_value = ApiHelper.deserialize_union_type(input_union_type, input_value, input_should_deserialize)
        assert actual_value == expected_value
