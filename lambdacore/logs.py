from contextlib import ContextDecorator
import functools
import logging
import os
import time

import structlog


logging.basicConfig(format="%(message)s",
                    level=logging.INFO)


def _add_service_context(_logger, _method, event_dict):
    """
    Function intended as a processor for structlog. It adds information about
    the service environment and reasonable defaults when not running in Lambda.
    """
    event_dict['function_name'] = os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'dev')
    event_dict['function_version'] = os.environ.get('AWS_LAMBDA_FUNCTION_VERSION', 0)
    event_dict['region'] = os.environ.get('AWS_REGION', os.uname().nodename)

    extras = ['SERVICE', 'STACK', 'STAGE']
    for extra in extras:
        if os.environ.get(extra):
            event_dict[extra.lower()] = os.environ[extra]

    return event_dict


structlog.configure_once(
    processors=[
        structlog.stdlib.add_log_level,
        _add_service_context,
        structlog.processors.TimeStamper(fmt='iso', utc=True, key='ts'),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True
)

logger = structlog.get_logger()

def log_invocation(func):
    """
    A decorator for Lambda handlers that logs the input event and the return
    value of the function. Easy and convenient way how to add more visibility
    to the runtime of your Lambdas.
    """

    @functools.wraps(func)
    def wrapper(event, context):
        try:
            logger.info('lambda invocation', invocation=event)
            result = func(event, context)
        except Exception as e: # pylint: disable=broad-except,invalid-name
            logger.error('execution error',
                         exc_info=e,
                         invocation=event,
                         function_name=context.function_name,
                         function_version=context.function_version,
                         aws_request_id=context.aws_request_id)
            raise e
        else:
            logger.info('lambda result', result=result)
            return result

    return wrapper


class log_duration(ContextDecorator): # pylint: disable=invalid-name
    """
    A context manager for measuring duration of the code inside its block.
    It can also be used as a decorator.

    It takes a single positional argument, the name of the logged event.
    By default, the duration value is logged under the 'duration' name, but
    you can pass in a 'duration_key' keyword argument to change it. Additional
    kwargs will be passed directly to the logger.

    The duration is measured in fractions of seconds using time.time().

    Usage:

    # as context manager
    with log_duration('calculation'):
        result = 1 + 1

    # as decorator
    @log_duration('http call', duration_key='http_time_spent', api_version='1.0')
    def make_http_call():
        pass

    """
    def __init__(self, event_name, duration_key='duration', **kwargs):
        self.start_time = 0
        self.event_name = event_name
        self.duration_key = duration_key
        self.logger_args = kwargs

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, *args):
        duration = time.time() - self.start_time
        self.logger_args[self.duration_key] = duration
        logger.info(self.event_name, **self.logger_args)
