import schema.management
from typing import Union, List


class SchemaAPI:
    def __init__(self):
        self.collection = schema.management.handle()

    def get_schema(self,
                   sense: str,
                   cat: Union[None, str] = None) -> dict:
        schema_filter = {"$or": [{"SPEECH-ACT": sense}]}

        filter = {
            "$and": [schema_filter]
        }

        if cat is not None:
            filter = {"$and": [{"CAT": cat}]}

        results = self.collection.find(filter)

        if results.count() == 0:
            raise Exception(f"Unknown schema {sense}.")

        out = {}
        for r in results:
            del r["_id"]
            out[r["SENSE"]] = r

        return out

    def list_senses(self, word: str) -> List[dict]:
        pass  # TODO implement list senses for schemata

    def get_sense(self, sense: str) -> dict:
        entry = self.collection.find_one({"SENSE": sense})

        if entry is None:
            raise Exception("Unknown sense " + sense + ".")

        del entry["_id"]

        return entry
