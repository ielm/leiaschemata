from schema.api import SchemaAPI
from schema.repository import Repo
from schema.schema import Schema
import unittest
from pprint import pprint


class SchemaTestCase(unittest.TestCase):

    def test_schema_build(self):
        schema = Repo().get_cat("REQUEST_ACTION")
        schema = Schema.build(schema)
        for elem in schema.elements():
            print(f"\n{elem.id}")
            pprint(elem.debug())