from collections import OrderedDict
from typing import Union
import schema.management


def mockSchema(
    sense: str,
    save: bool = True,
    collection=None,
    definition: str = "",
    example: str = "",
    comments: str = "",
    tmrhead: str = "NIL",
    synstruc: Union[OrderedDict, str] = "",
    semstruc: Union[OrderedDict, str] = "",
    outputsyntax: str = "NIL",
    meaningprocedures: str = "NIL",
    examplebindings: str = "NIL",
    exampledeps: str = "NIL",
    # synonyms: str = "NIL",
    # hyponyms: str = "NIL",
    **kwargs) -> OrderedDict:

    tag = sense.split("-")[0]
    cat = ''.join(i for i in sense.split("-")[1] if not i.isdigit())

    if isinstance(synstruc, str):
        if synstruc == "":
            synstruc = OrderedDict()

    if isinstance(semstruc, str):
        if semstruc == "":
            semstruc = OrderedDict()

    entry = OrderedDict([
        ("SENSE", sense),
        ("TAG", tag ),
        ("CAT", cat),
        ("DEF", definition),
        ("EX", example),
        ("COMMENTS", comments),
        ("TMR-HEAD", tmrhead),
        ("SYN-STRUC", synstruc),
        ("SEM-STRUC", semstruc),
        ("OUTPUT-SYNTAX", outputsyntax),
        ("MEANING-PROCEDURES", meaningprocedures),
        ("EXAMPLE-BINDINGS", examplebindings),
        ("EXAMPLE-DEPS", exampledeps),
        # ("SYNONYMS", synonyms),
        # ("HYPONYMS", hyponyms),
    ])

    for key, value in kwargs.items():
        entry[key] = value

    if save:
        if collection is None:
            collection = schema.management.handle()
        collection.insert_one(entry)
        del entry["_id"]

    return entry
