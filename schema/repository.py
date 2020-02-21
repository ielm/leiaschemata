import json
import os
import urllib.request

from collections import OrderedDict


class Repo:
    def __init__(self, host=None, port=None, cookie=None):
        self.host = host
        if self.host is None:
            self.host = os.environ[
                "REPO_HOST"] if "REPO_HOST" in os.environ else "localhost"

        self.port = port
        if self.port is None:
            self.port = int(os.environ["REPO_PORT"]
                            ) if "REPO_PORT" in os.environ else 5005

        self.cookie = cookie

    def __rget(self, path, params=None):
        url = f"http://{self.host}:{str(self.port)}{path}"
        print(url)

        def __format_param(key):
            values = params[key]
            if type(values) is not list:
                values = [values]

            return "&".join(map(lambda value: key + "=" + str(value), values))

        if len(params) > 0:
            # url = url + "?" + "&".join(map(__format_param, params.keys()))
            url = f"{url}?{'&'.join(map(__format_param, params.keys()))}"

        request = urllib.request.Request(url)
        if self.cookie is not None:
            request.add_header("cookie", self.cookie)

        contents = None
        with urllib.request.urlopen(request) as response:
            contents = response.read()
            self.cookie = response.headers.get("Set-Cookie")
        return contents

    def __contains__(self, item):
        try:
            self.get_schema(item)
            return True
        except Exception:
            return False

    def __getitem__(self, item):
        return self.get_schema(item)

    def get_sense(self, sense):
        results = self.__rget("/schema/api/sense", params={"sense": sense})
        return json.loads(results, object_pairs_hook=OrderedDict)

    def get_schema(self, tag, cat=None):
        params = {"tag": tag}
        if cat is not None:
            params["cat"] = cat

        results = self.__rget("/schema/api/schema", params=params)
        return json.loads(results, object_pairs_hook=OrderedDict)

    def get_cat(self, cat, tag=None):
        params = {"cat": cat}
        if tag is not None:
            params["tag"] = tag

        results = self.__rget("/schema/api/cat", params=params)
        return json.loads(results, object_pairs_hook=OrderedDict)

    def list_senses(self, tag):
        results = self.__rget("/schema/api/list", params={"tag": tag})
        return json.loads(results)

    def search(self, name):
        results = self.__rget("/schema/api/search", params={"name": name})
        return json.loads(results, object_pairs_hook=OrderedDict)
