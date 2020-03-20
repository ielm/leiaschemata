from ontograph.Frame import Frame
from ontoagent.engine.signal import Signal, TMR
from lex.lexeme import Lexeme
from typing import List
from collections import OrderedDict
from typing import Union


class Schema(Signal):

    @classmethod
    def build(cls, sdict: OrderedDict, tmr: TMR) -> 'Schema':
        anchor = Frame("@IO.SCHEMA.?")
        anchor.add_parent("@ONT.SCHEMA")
        space = Schema.next_available_space("SCHEMA")
        root = sdict["CAT"].upper()
        root = Frame(f"@{space.name}.{root}.?")

        s = super().build(root, space=space, anchor=anchor)
        s = Schema(s.anchor)
        s.__build(sdict)
        # s.__link_tmr(tmr)
        return s

    def element(self, name: str):
        try:
            return self.root()["HEAD"].singleton()
        except KeyError:
            print(f"{name} is not defined")

    def elements(self) -> List[Frame]:
        return list(self.anchor["HAS-ELEMENT"])

    def add_element(self, element: Frame):
        self.anchor["HAS-ELEMENT"] += element
        self.add_constituent(element)

    def add_tmr_element(self, element: str, tmr_element: Frame):
        self.root()[element].singleton()["TMR_ELEMENT"] = tmr_element

    def head(self):
        return self.root()["HEAD"].singleton()

    def debug(self) -> dict:
        out = {}
        for constituent in self.constituents():
            results = {}
            for slot in constituent.slots():
                results[slot.property] = slot.debug()
            out[constituent.id] = results
        return out

    def intersect(self, element: Frame, lexemes: list):
        temp = []
        if isinstance(element, Frame):
            for l in lexemes:
                if l["CAT"] == element["CAT"]:
                    temp.append(Lexeme.build(l))
        lex_candidates = []
        for candidate in temp:
            if self.syn_match(candidate, mode="STRICT"):
                if self.sem_match(candidate, mode="STRICT"):
                    lex_candidates.append(candidate)
        return lex_candidates

    def syn_match(self, candidate: Lexeme, mode: str = "STRICT") -> bool:
        match = False
        if mode is "STRICT":
            l_seen = []
            s_seen = []
            for l_elem in candidate.elements():
                for s_elem in self.elements():
                    s_id = str(s_elem.id).split('.')[1]
                    l_id = str(l_elem.id).split('.')[1]
                    if (s_id == "HEAD" and l_id == "ROOT") or s_id == l_id:
                        s_seen.append(s_elem)
                        l_seen.append(l_elem)
            if not list(set(self.elements()) - set(s_seen)) and \
                    not list(set(candidate.elements()) - set(l_seen)):
                match = True
        return match

    def sem_match(self, candidate: Lexeme, mode: str = "STRICT") -> bool:
        return True

    def __build(self, content):

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

        for meta in content.keys():
            if meta != "SYN-STRUC" and meta != "SEM-STRUC":
                self.anchor[meta] = content[meta]

        for e in self.elements():
            for f in e.get_slot("SEM").facets():
                if list(f.list())[0] in element_vars.keys():
                    e.get_slot("SEM").get_facet(f.type).assign_filler(
                        element_vars[list(f.list())[0]])

    # def __link_tmr(self, tmr: TMR):
    #     # tmr_elements = list(map(lambda c: c, tmr.constituents()))
    #     # print(tmr_elements)
    #     # print(list(map(lambda c: c.debug(), tmr_elements)))
    #     # seen = []
    #     # for element in self.constituents():
    #     #     print(element.debug())
    #     #     if element.id
    #     #     pass
    #     pass
