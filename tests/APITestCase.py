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
        self.assertEqual(schema, {
            "MY_SCHEMA-REQ_ACT1": sense1,
            "MY_SCHEMA-REQ_INFO1": sense2
        })
        with self.assertRaises(Exception):
            SchemaAPI().get_schema("no-such-schema")

        sense3 = mockSchema("MY_SCHEMA-REQ_ACT2")

        schema = SchemaAPI().get_schema("MY_SCHEMA", cat="REQ_ACT")
        self.assertEqual(schema, {
            "MY_SCHEMA-REQ_ACT1": sense1,
            "MY_SCHEMA-REQ_ACT2": sense3
        })

    def test_list_senses(self):
        sense1 = mockSchema("MY_SCHEMA-REQ_ACT1")
        sense2 = mockSchema("MY_SCHEMA-REQ_ACT2")
        sense3 = mockSchema("NO_SCHEMA-REQ_ACT1")

        senses = SchemaAPI().list_senses("MY_SCHEMA")
        self.assertTrue(sense1["SENSE"] in senses)
        self.assertTrue(sense2["SENSE"] in senses)
        self.assertFalse(sense3["SENSE"] in senses)
        with self.assertRaises(Exception):
            SchemaAPI().list_senses("no-such-schema")

    def test_get_sense(self):
        sense1 = mockSchema("MY_SCHEMA-REQ_ACT1")
        sense2 = mockSchema("MY_SCHEMA-REQ_ACT2")

        self.assertEqual(sense1, SchemaAPI().get_sense("MY_SCHEMA-REQ_ACT1"))
        self.assertEqual(sense2, SchemaAPI().get_sense("MY_SCHEMA-REQ_ACT2"))
        with self.assertRaises(Exception):
            SchemaAPI().get_sense("no_such_schema-req_act1")

    def test_search(self):
        sense1 = mockSchema("MY_SCHEMA-REQ_ACT1", definition="1")
        sense2 = mockSchema("MY_SCHEMA-REQ_ACT2", definition="2")
        sense3 = mockSchema("NO_SCHEMA-REQ_ACT1", definition="3")

        senses = SchemaAPI().search("MY")
        self.assertTrue(
            sense1["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertTrue(
            sense2["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertFalse(
            sense3["SENSE"] in map(lambda sense: sense["SENSE"], senses))

        senses = SchemaAPI().search("NO")
        self.assertFalse(
            sense1["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertFalse(
            sense2["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertTrue(
            sense3["SENSE"] in map(lambda sense: sense["SENSE"], senses))

        senses = SchemaAPI().search("*")
        self.assertTrue(
            sense1["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertTrue(
            sense2["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertTrue(
            sense3["SENSE"] in map(lambda sense: sense["SENSE"], senses))

        senses = SchemaAPI().search("SCHEMA")
        self.assertTrue(
            sense1["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertTrue(
            sense2["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertTrue(
            sense3["SENSE"] in map(lambda sense: sense["SENSE"], senses))

        senses = SchemaAPI().search("XYZ")
        self.assertFalse(
            sense1["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertFalse(
            sense2["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertFalse(
            sense3["SENSE"] in map(lambda sense: sense["SENSE"], senses))

        senses = SchemaAPI().search("MY_SCHEMA-REQ_ACT1", include_fields=["DEF"])
        self.assertEqual(1, len(senses))
        self.assertEqual(2, len(senses[0].keys()))
        self.assertTrue("SENSE" in senses[0])
        self.assertTrue("DEF" in senses[0])

        senses = SchemaAPI().search("MY", page_size=1, page=0)
        self.assertTrue(
            sense1["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertFalse(
            sense2["SENSE"] in map(lambda sense: sense["SENSE"], senses))
        self.assertFalse(
            sense3["SENSE"] in map(lambda sense: sense["SENSE"], senses))
