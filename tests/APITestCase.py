from schema.api import SchemaAPI
from pymongo import MongoClient
from collections import OrderedDict
from tests.TestUtils import mockSchema

import unittest


class SchemaAPITestCase(unittest.TestCase):
    def setUp(self):
        import schema.management
        import os

        schema.management.DATABASE = "unittest"
        os.environ[schema.management.SCHEMA_ACTIVE] = "unittest"

    def tearDown(self):
        MONGO_HOST = "localhost"
        MONGO_PORT = 27017
        DATABASE = "unittest"

        client = MongoClient(MONGO_HOST, MONGO_PORT)
        client.drop_database(DATABASE)

    def test_get_schema(self):
        sense1 = mockSchema("MY_SCHEMA-REQ_ACT1")
        sense2 = mockSchema("MY_SCHEMA-REQ_INFO1")

        schema = SchemaAPI().get_schema("MY_SCHEMA")
        self.assertEqual(schema, {"MY_SCHEMA-REQ_ACT1": sense1, "MY_SCHEMA-REQ_INFO1": sense2})
        with self.assertRaises(Exception):
            SchemaAPI().get_schema("no-such-schema")

        sense3 = mockSchema("MY_SCHEMA-REQ_ACT2")

        schema = SchemaAPI().get_schema("MY_SCHEMA", cat="REQ_ACT")
        self.assertEqual(schema, {"MY_SCHEMA-REQ_ACT1": sense1, "MY_SCHEMA-REQ_ACT2": sense3})