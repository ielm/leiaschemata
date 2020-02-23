from ontograph.Frame import Frame
from ontograph.Space import Space
from ontoagent.engine.signal import Signal
from typing import Dict, List, Union
from collections import OrderedDict


class Element(Frame):

    def null(self):
        pass


class Schema(Signal):
    # Has an anchor and a root. The root is the speech-act of the schema, which has
    # slots for all elements in the schema such as the SUBJ, HEAD, and DOBJ.

    @classmethod
    def build(cls, sdict: OrderedDict):
        sdict = sdict[f"{list(sdict.keys())[0]}"]
        anchor = Frame("@IO.SCHEMA.?")
        anchor.add_parent("@ONT.SCHEMA")
        space = Schema.next_available_space("SCHEMA")
        root = sdict["CAT"].upper()
        root = Frame(f"@{space.name}.{root}.?")

        s = super().build(root, space=space, anchor=anchor)
        s = Schema(s.anchor)
        s._build(sdict)

        return s

    def _build(self, content):
        def _construct_element(_id, _space, _content):
            elem = Element(f"@{_space}.{_id}.?")

            for item in list(_content["SYN-STRUC"].items()):
                elem[item[0]] = item[1]
            for item in list(_content["SEM-STRUC"].items()):
                elem["SEM"] = item[0]
                if item[1]:
                    for relation in item[1].items():
                        elem["SEM"][relation[0]] = list(relation[1].items())[0][1]
            return elem

        for e in content["SYN-STRUC"]:
            strucs = {
                "SYN-STRUC": content["SYN-STRUC"][e],
                "SEM-STRUC": content["SEM-STRUC"][e]
            }
            element = _construct_element(e, self.space().name, strucs)
            self.root()[e] = element
            self.add_element(element)

    def elements(self) -> List[Frame]:
        return list(self.anchor["HAS-ELEMENT"])

    def add_element(self, element: Element):
        self.anchor["HAS-ELEMENT"] += element


class Filter:

    def __init__(self):
        pass
