
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
    s.__link_tmr(tmr)
    return s

  ##############################################################
  # -----------------------  UTILITIES  ---------------------- #
  ##############################################################

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
    IGNORE = ["AUX", "ADV"]
    if mode == "STRICT":
      l_seen = []
      s_seen = []
      for l_elem in candidate.elements():
        for s_elem in self.elements():
          s_id = str(s_elem.id).split('.')[1]
          l_id = str(l_elem.id).split('.')[1]
          if (s_id == "HEAD" and l_id == "ROOT") or s_id == l_id:
            s_seen.append(s_elem)
            l_seen.append(l_elem)

      if not list(set([s.id for s in self.elements() if \
        s.id.split('.')[1] not in IGNORE]) - set(s_seen)) and \
          not list(set([l.id for l in candidate.elements() if \
            l.id.split('.')[1] not in IGNORE]) - set(l_seen)):
        match = True
    return match


  ##############################################################
  # -----------------------  INTERNAL  ----------------------- #
  ##############################################################

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
          if isinstance(item[1], OrderedDict):
            for relation in item[1].items():
              if isinstance([relation[1]], list):
                elem["SEM"][relation[0]] = relation[1]
              elif isinstance([relation[1], OrderedDict]):
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
      for f in e.get_slot("SEM").facets():  # Get slots
        if isinstance(list(f.list())[0], list):
          if list(f.list())[0] in element_vars.keys():
            e.get_slot("SEM").get_facet(f.type).assign_filler(
              element_vars[list(f.list())[0]])


  def __link_tmr(self, tmr: TMR):
    def is_speech_act(element: Union[str, Frame]):
      speech_acts = ["REQUEST_ACTION", "REQUEST_INFO", "INFORM"]
      s = element.id if isinstance(element, Frame) else element
      return True if True in list(map(lambda sa: sa in s, speech_acts)) else False

    def get_tmr_element(schema_element: Frame, tmr: TMR):
      if is_speech_act(schema_element):
        if tmr.root().id.split(".")[1].replace("-", "_") in schema_element.id:
          return tmr.root()
      elif "SUBJECT" in schema_element.id:
        return tmr.root()["THEME"].singleton()["AGENT"].singleton()
      elif "HEAD" in schema_element.id:
        return tmr.root()["THEME"].singleton()
      elif "DIRECTOBJECT" in schema_element.id:
        root = tmr.root()["THEME"].singleton()
        return root["THEME"].singleton()
      elif "OBJECT" in schema_element.id:
        root = tmr.root()["THEME"].singleton()
        return root["DESTINATION"].singleton()
      return None

    for element in self.constituents():
      tmr_element = get_tmr_element(element, tmr)
      if tmr_element != None:
        element["TMR_ELEMENT"] = tmr_element
        elemid = element["TMR_ELEMENT"].singleton().id.split(".")[1].replace("-", "_")
        if elemid not in self.root().id:
          if elemid in WordCache:
            wordtag = WordCache[elemid][0]
            if '@' in wordtag:
              word = Lexeme.from_frame(wordtag)
              element["LEX"] = word.anchor
            else:
              word = Lexeme.build(Lexicon().get_sense(wordtag))
              element["LEX"] = word.anchor
      elif "ROOT-WORD" in element:
        word =  Lexeme.build(Lexicon().get_sense(element["ROOT-WORD"].singleton()))
        element["LEX"] = word.anchor
