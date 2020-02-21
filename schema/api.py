import schema.management
from typing import Union, List, Dict


class SchemaAPI:
    def __init__(self):
        self.collection = schema.management.handle()

    def get_schema(self, tag: str, cat: Union[None, str] = None) -> dict:
        schema_filter = {"$or": [{"TAG": tag}]}

        filter = {"$and": [schema_filter]}

        if cat is not None:
            filter = {"$and": [{"CAT": cat}]}

        results = self.collection.find(filter)

        if results.count() == 0:
            raise Exception(f"Unknown schema {tag}.")

        out = {}
        for r in results:
            del r["_id"]
            out[r["SENSE"]] = r

        return out

    def get_cat(self, cat: str, constraints: Union[Dict[str, str], None]=None) -> dict:
        cat_filter = {"$match": {"CAT": cat}}

        # filter = {
        #     "$and": [cat_filter]
        # }

        # if constraints is not False:
        #     for key in constraints.keys():
        #         if key.upper() not in ["SEM-STRUC", "SYN-STRUC"]:
        #             filter["$and"].append({f"{key.upper()}": constraints[key].upper()})
                    
        #     pass

        sort = {"$sort": {"SENSE": 1}}

        results = list(self.collection.aggregate([cat_filter, sort]))

        if len(results) == 0:
            raise Exception(f"Unknown speech act {cat}.")

        out = {}
        for r in results:
            del r["_id"]
            out[r["SENSE"]] = r

        return out

    def list_senses(self, tag: str) -> List[dict]:
        match = {"$match": {"TAG": tag}}

        group = {"$group": {"_id": tag, "senses": {"$push": "$SENSE"}}}

        aggregation = [match, group]

        results = list(self.collection.aggregate(aggregation))

        if len(results) == 0:
            raise Exception(f"Unknown schema {tag}.")

        return results[0]["senses"]

    def get_sense(self, sense: str) -> dict:
        entry = self.collection.find_one({"SENSE": sense})

        if entry is None:
            raise Exception(f"Unknown schema sense {sense}.")

        del entry["_id"]

        return entry

    def search(self,
               partial_name: str,
               include_fields: Union[List[str], None] = None,
               page_size=100,
               page: Union[int, None] = None) -> List[dict]:

        regex = f".*{partial_name}.*" if partial_name != "*" else ".*"
        match = {"$match": {"SENSE": {"$regex": regex}}}
        sort = {"$sort": {"SENSE": 1}}
        aggregation = [match, sort]

        if include_fields is not None:
            project = {"$project": {"SENSE": 1}}

            for field in include_fields:
                project["$project"][field] = 1

            aggregation.append(project)

        if page is not None:
            skip = {"$skip": (page * page_size)}
            limit = {"$limit": page_size}
            aggregation.append(skip)
            aggregation.append(limit)

        results = list(self.collection.aggregate(aggregation))
        for r in results:
            del r["_id"]

        return results

    def save(self, name: str, sense: dict):
        tag = name.split("-")[0]
        cat = ''.join(i for i in name.split("-")[1] if not i.isdigit())

        sense["SENSE"] = name
        sense["TAG"] = tag
        sense["CAT"] = cat

        self.collection.delete_one({"SENSE": name})
        self.collection.insert_one(sense)

        del sense["_id"]

    def delete(self, sense: str):
        self.collection.delete_one({"SENSE": sense})
