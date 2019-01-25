import collections
import json
import sys
import uuid

import pytest

from core import log_invocation


# mock of the context object that gets passed into the handler
# https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
Context = collections.namedtuple('Context',
                                 ['function_name',
                                  'function_version',
                                  'aws_request_id'])


def load_log_events(caplog):
    return [json.loads(record[2]) for record in caplog.record_tuples]

def assert_service_context(log_record):
    assert 'function_name' in log_record
    assert 'function_version' in log_record
    assert 'region' in log_record

@pytest.mark.parametrize('ret_val', [1, None])
def test_log_invocation_decorator(caplog, ret_val):
    f_name = sys._getframe().f_code.co_name
    invocation_context = Context(function_name=f_name,
                                 function_version='$LATEST',
                                 aws_request_id=str(uuid.uuid4()))

    @log_invocation
    def handler(*_args):
        return ret_val

    assert handler({}, invocation_context) == ret_val

    invocation_log, result_log = load_log_events(caplog)
    assert 'invocation' in invocation_log
    assert_service_context(invocation_log)
    assert 'result' in result_log
    assert_service_context(result_log)

def test_log_invocation_decorator_throwing(caplog):
    f_name = sys._getframe().f_code.co_name
    invocation_context = Context(function_name=f_name,
                                 function_version='$LATEST',
                                 aws_request_id=str(uuid.uuid4()))

    @log_invocation
    def handler(*_args):
        raise RuntimeError('No can do')

    with pytest.raises(RuntimeError):
        handler({}, invocation_context)

    invocation_log, error_log = load_log_events(caplog)
    assert 'invocation' in invocation_log
    assert_service_context(invocation_log)
    assert 'invocation' in error_log
    assert 'exception' in error_log
    assert 'aws_request_id' in error_log
    assert_service_context(error_log)
