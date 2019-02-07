import functools
import logging
import os

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

# I couldn't get structlog and capsys to cooperate in tests
# hence I'm using the stdlib logger in tests so that caplog can
# capture it and logging via printing to stdout in production
_logger_factory = structlog.stdlib.LoggerFactory() \
    if os.environ.get('AWS_REGION') is None \
       else structlog.PrintLoggerFactory()

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
    logger_factory=_logger_factory,
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
