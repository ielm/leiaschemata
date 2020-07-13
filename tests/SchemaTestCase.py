from ontoagent.engine.xmr import TMR
from ontograph.Frame import Frame
from ontograph_ontolang.OntoLang import OntoLang
from ontogen.schema import link_tmr
from schema.api import SchemaAPI
from schema.repository import Repo
from schema.newschema import Schema
from lex.lexicon import Lexicon
import unittest
# from ontoagent.utils.analysis import TextAnalyzer
from pprint import pprint


class SchemaTestCase(unittest.TestCase):

    def test_schema_build(self):
        # analyzer = TextAnalyzer()
        with open('tests/resources/GetTheRedBlock.knowledge', 'r') as ontosem:
            # analyzer.cache("Get the red block.", str(ontosem.read()))
            OntoLang().run(str(ontosem.read()))
        # tmr = analyzer.to_signal("Get the red block.")
        tmr = TMR.instance()
        tmr.set_root(Frame("@TMR#1.REQUEST-ACTION.1"))
        # print(tmr.root().debug())
        repo = Repo().get_cat(tmr.root().id.split(".")[1].replace("-", "_"))
        schemata = {}
        for key in repo.keys():
            s = Schema.instance()
            s.populate(repo[key])
            s = link_tmr(s, tmr)
            schemata[key] = s
        # for i, s in zip(schemata.keys(), schemata.items()):
            # print(f"{i}: {s[1].debug()}")
        self.assertEqual(2, len(schemata))
        schema_keys = [str(key) for key in schemata.keys()]
        self.assertEqual(len(schema_keys), 2)
        self.assertEqual(schema_keys[0], "DITRANSITIVE-REQUEST_ACTION1")
        self.assertEqual(schema_keys[1], "MONOTRANSITIVE-REQUEST_ACTION1")

        pprint(schemata)

