import datetime
import enum
import json
import math

import pytest

from core import StandardSerializer


@pytest.fixture()
def make_file_discoverable():
    # for the deserialization to work, the objects have to be
    # importable; this fixture adds the file directory into
    # sys.path to enable that
    import os, sys
    here_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(here_dir)


class Primitive:
    deserialized_types = {
        'a_number': 'int',
        'a_float': 'float',
        'a_string': 'str',
        'a_boolean': 'bool',
        'a_date': 'date',
        'a_datetime': 'datetime'
    }

    def __init__(self):
        self.a_number = 1
        self.a_float = math.pi
        self.a_string = 'hello world'
        self.a_boolean = True
        self.a_date = datetime.date.today()
        self.a_datetime = datetime.datetime.utcnow()


class Animals(enum.Enum):
    DOG = 'woof'
    CAT = 'meow'
    SNAKE = 'ssssh'


class Compound:
    deserialized_types = {
        'list_of_strings': 'list[str]',
        'tuple_of_primitives': 'list[test_serializer.Primitive]',
        'an_enum': 'test_serializer.Animals'
    }

    def __init__(self):
        self.list_of_strings = ['spam', 'spam', 'spam', 'Spanish Inquisition']
        self.tuple_of_primitives = (Primitive(), Primitive())
        self.an_enum = Animals.SNAKE


class CustomAttribute:
    deserialized_types = {
        'a_number': 'int'
    }

    attribute_map = {
        'a_number': 'aNumber'
    }

    def __init__(self):
        self.a_number = 1


def test_serialization_of_primitive_object():
    serializer = StandardSerializer()
    primitive = Primitive()

    serialized = serializer.serialize(primitive)

    assert isinstance(serialized, dict)
    assert serialized['a_number'] == primitive.a_number
    assert serialized['a_float'] == primitive.a_float
    assert serialized['a_string'] == primitive.a_string
    assert serialized['a_boolean'] == primitive.a_boolean
    assert serialized['a_date'] == primitive.a_date.isoformat()
    assert serialized['a_datetime'] == primitive.a_datetime.isoformat()


def test_serialization_of_compound_object(make_file_discoverable):
    serializer = StandardSerializer()
    primitive = Primitive()
    original = Compound()

    serialized = serializer.serialize(original)

    assert isinstance(serialized, dict)
    assert serialized['list_of_strings'] == original.list_of_strings
    assert len(serialized['tuple_of_primitives']) == 2
    assert serialized['tuple_of_primitives'][0]['a_number'] == primitive.a_number
    assert serialized['an_enum'] == original.an_enum.value

    as_json = json.dumps(serialized)
    deserialized = serializer.deserialize(as_json, Compound)

    assert isinstance(deserialized, Compound)
    assert deserialized.list_of_strings == original.list_of_strings
    assert deserialized.an_enum.value == original.an_enum.value

def test_serialization_with_attribute_remapping():
    serializer = StandardSerializer()
    original = CustomAttribute()

    serialized = serializer.serialize(original)

    assert isinstance(serialized, dict)
    assert serialized['aNumber'] == original.a_number

    as_json = json.dumps(serialized)
    deserialized = serializer.deserialize(as_json, CustomAttribute)

    assert isinstance(deserialized, CustomAttribute)
    assert deserialized.a_number == original.a_number
