from ontograph.Frame import Frame
from ontoagent.engine.signal import Signal
from typing import List
from collections import OrderedDict


class Schema(Signal):

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

        element_vars = {}

        def _construct_element(_id, _space, _content):
            elem = Frame(f"@{_space}.{_id}.?")

            for item in list(_content["SYN-STRUC"].items()):
                elem[item[0]] = item[1]  # add syntactic constraints
                if item[0] == "ROOT":
                    element_vars[item[1]] = elem
            for item in list(_content["SEM-STRUC"].items()):
                elem["SEM"] = item[0]  # add semantic constraint
                if item[1]:  # if case-role constraints exist
                    for relation in item[1].items():
                        elem["SEM"][relation[0]] = list(
                            relation[1].items())[0][1]
            return elem

        for e in content["SYN-STRUC"]:
            strucs = {
                "SYN-STRUC": content["SYN-STRUC"][e],
                "SEM-STRUC": content["SEM-STRUC"][e]
            }
            element = _construct_element(e, self.space().name, strucs)

            self.root()[e] = element
            self.add_element(element)

        for e in self.elements():
            for f in e.get_slot("SEM").facets():
                if list(f.list())[0] in element_vars.keys():
                    e.get_slot("SEM").get_facet(f.type).assign_filler(
                        element_vars[list(f.list())[0]])

    def elements(self) -> List[Frame]:
        return list(self.anchor["HAS-ELEMENT"])

    def add_element(self, element: Frame):
        self.anchor["HAS-ELEMENT"] += element
        self.add_constituent(element)