# lambda-layer-core
An AWS Lambda Layer of various core functions I use all the time in my Lambda functions.

[![Build Status](https://travis-ci.com/milancermak/lambda-layer-core.svg?branch=master)](https://travis-ci.com/milancermak/lambda-layer-core)

## Modules

### logs
Provides two useful tools for logging.

###### log_invocation
`@log_invocation` is decorator intended to be used on the Lambda handler. It logs the invocation event (input) and the result (output) of Lambda function. If it raises an exception, it logs it as an error together with additional debug information and re-raises it.

Example usage:
```python
from core import log_invocation

@log_invocation
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello world!'
    }
```

##### logger
As the name suggests, `logger` is a log interface built on [`structlog`](https://www.structlog.org/en/stable/). It provides structured (JSON) logging of events. This allows to for easy processing and analysis later.

Example usage:
```python
from core import logger

def foo():
    try:
        logger.info('computing')
        1 / 0
    except ZeroDivisionError as exc:
        logger.error('nope', exc_info=exc)
```
The logged events are have a `ts` key with the current timestamp, `function_name`, `function_version` and `region` keys comming from the [Lambda execution environment](https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html). Additionally, if you declare `SERVICE`, `STACK` or `STAGE` envvars (a practice I always follow), they will be logged (with lowercased keys) in the event as well.

### serializer

##### StandardSerializer class
The `StandardSerializer` is intended for serializing and deserializing native Python classes to and from JSON. This is especially useful when you want to store your models in DynamoDB.

Example usage:
```python
import enum, json
from core import StandardSerializer

serializer = StandardSerializer()

class Sport(enum.Enum):
    SPRINT = 'Sprint'
    JUMP = 'Jump'
    THROW = 'Throw'

class Athlete:
    deserialized_types = {
        'name': 'string',
        'age': 'int',
        'sport': 'Sport'
    }

    # attribute_map is optional
    attribute_map = {
        'name': 'athleteName',
        'age': 'athleteAge',
        'sport': 'athleteSport'
    }

    def __init__(self, name, age, sport):
        self.name = name
        self.age = age
        self.sport = sport

jay = Athlete('Jay', 20, Sport.JUMP)
se_jay = serializer.serialize(jay) # {'athleteName': 'Jay', 'athleteAge': 20, 'athleteSport': 'Jump'}
# se_jay can now be used with boto3 dynamodb.put_item or json.dumps

jay_again = serializer.deserialize(json.dumps(se_jay), Athlete) # jay, recreated
```
The only necessary part to make a class compatible with the serializer is the `deserialized_types` variable. It's a mapping between the name of the attribute and the type it is (de)serialized to/from. It can also be another class, as long as it's `import`able. See the [test file](tests/test_serializer.py) for more (senseless) examples. The `attribute_map` serves as a translation map between the attribute names of the Python class and those used in the resulting dictionary (eventually JSON).

For even greater convenience, I recommend using the great [attrs](http://attrs.org/) library to build your models.

## Building & publishing the layer

There are two shell scripts in the repo. First, `build_archive.sh` creates a `layer.zip` file that contains the files in the [necessary structure](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path) for the layer to work in Lambda. The second, `publish_layer.sh` is just an AWS CLI command that makes the layer available for use.
