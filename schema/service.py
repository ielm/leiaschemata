import json
import os

from collections import OrderedDict
from flask import abort, Flask, request, render_template, redirect, session
from flask_cors import CORS
from flask_socketio import SocketIO
from schema.api import SchemaAPI
from schema.management import active, handle

app = Flask(__name__, template_folder="../ui/templates/")
CORS(app)
socketio = SocketIO(app)

app.secret_key = "leia-repo-service"

EDITING_ENABLED = os.environ["EDITING_ENABLED"].lower() == "true" if "EDITING_ENABLED" in os.environ else True


def env_payload():
    if "editing" not in session:
        session["editing"] = False

    return {
        "editing_enabled": EDITING_ENABLED,
        "active_repo": active(),
        "editing": session["editing"] and EDITING_ENABLED,
    }


### /service/api - routes for query, returning JSON formatted results


@app.route("/schema/api/sense", methods=["GET"])
def api_sense():
    if "sense" not in request.args:
        return "Parameter 'sense' required.", 403

    try:
        sense = request.args["sense"]
        entry = SchemaAPI().get_sense(sense)
        return json.dumps(entry)
    except Exception:
        return "No such sense.", 404


@app.route("/schema/api/schema", methods=["GET"])
def api_schema():
    if "tag" not in request.args:
        return "Parameter 'tag' required.", 403

    cat = None
    if "cat" in request.args:
        cat = request.args["cat"]

    try:
        tag = request.args["tag"]
        results = SchemaAPI().get_schema(tag=tag, cat=cat)
    except Exception:
        return "No such schema.", 404
    return json.dumps(results)

@app.route("/schema/api/cat", methods=["GET"])
def api_cat():
    if "cat" not in request.args:
        return "Parameter 'cat' required.", 403

    tag = None
    if "tag" in request.args:
        tag = request.args["tag"]

    try:
        cat = request.args["cat"]
        results = SchemaAPI().get_cat(cat=cat, tag=tag)
    except Exception:
        return "No such schema.", 404
    return json.dumps(results)

@app.route("/schema/api/list", methods=["GET"])
def api_list():
    if "tag" not in request.args:
        return "Parameter 'tag' required.", 403

    tag = request.args["tag"]
    results = SchemaAPI().list_senses(tag)
    return json.dumps(results)


@app.route("/schema/api/search", methods=["GET"])
def api_search():
    if "name" not in request.args:
        return "Parameter 'name' required.", 403

    name = request.args["name"]

    include_fields = None
    if "include" in request.args:
        include_fields = request.args.getlist("include")

    page_size = 100
    page = None
    if "pagesize" in request.args:
        page_size = int(request.args["pagesize"])
    if "page" in request.args:
        page = int(request.args["page"])

    results = SchemaAPI().search(name,
                                 include_fields=include_fields,
                                 page_size=page_size,
                                 page=page)
    return json.dumps(results)


### /schema/view - routes for the editor and browser ui, GET only


@app.route("/schema/view/", methods=["GET"])
def view():
    page = 0
    senses = SchemaAPI().search("*", include_fields=["DEF"], page=page)

    return render_template("editor.html", senses=senses, page=page, env=env_payload())


@app.route("/schema/view/toggle/editing")
def view_toggle_editing():
    if "editing" not in session:
        session["editing"] = False

    session["editing"] = not session["editing"]

    return "OK"


### /schema/edit - routes for the editor api, POST only


@app.route("/schema/edit/save/<sense>", methods=["POST"])
def edit_save(sense):
    if not EDITING_ENABLED:
        abort(403)

    data = json.loads(request.data, object_pairs_hook=OrderedDict)

    SchemaAPI().save(sense, data)
    return "OK"


@app.route("/schema/edit/delete/<sense>", methods=["POST"])
def edit_delete(sense):
    if not EDITING_ENABLED:
        abort(403)

    SchemaAPI().delete(sense)
    return "OK"


### /lexicon/manage - routes for the version management system


@app.route("/schema/manage", methods=["GET"])
def manage():

    message = request.args["message"] if "message" in request.args else None
    error = request.args["error"] if "error" in request.args else None

    from schema.management import active, list_collections, list_local_archives, list_remote_archives, ARCHIVE_PATH
    payload = {
        "active": active(),
        "installed": list_collections(),
        "local": list(list_local_archives()),
        "remote": list(list_remote_archives()),
        "local-volume": ARCHIVE_PATH,
        "message": message,
        "error": error
    }

    return render_template("manager.html", payload=payload, env=env_payload())


@app.route("/schema/manage/activate", methods=["POST"])
def manage_activate():

    repo = request.form["repository"]

    try:
        from schema.management import activate
        activate(repo)
    except Exception as e:
        return redirect("/manage?error=" + e.message)

    return redirect("/schema/manage")

@app.route("/schema/manage/copy", methods=["POST"])
def manage_copy():

    name = request.form["name"]
    repo = request.form["repository"]

    try:
        from schema.management import copy_collection
        copy_collection(repo, name)
    except Exception as e:
        return redirect("/schema/manage?error=" + e.message)

    message = f"Copied {repo} to {name}."
    return redirect("/schema/manage?message=" + message)

@app.route("/schema/manage/rename", methods=["POST"])
def manage_rename():

    name = request.form["name"]
    repo = request.form["repository"]

    try:
        from schema.management import rename_collection
        rename_collection(repo, name)
    except Exception as e:
        return redirect("/schema/manage?error=" + e.message)

    message = f"Renamed {repo} to {name}."
    return redirect("/schema/manage?message=" + message)

@app.route("/schema/manage/archive", methods=["POST"])
def manage_archive():

    print(request.args)

    name = request.form["name"]
    repo = request.form["repository"]

    filename = name + ".gz"

    try:
        from schema.management import collection_to_file, list_collections, rename_collection, ARCHIVE_PATH

        if name != repo and name in list_collections():
            raise Exception("Cannot archive using another name that already exists.")

        path = os.environ[ARCHIVE_PATH] if ARCHIVE_PATH in os.environ else None

        if path is None:
            raise Exception("Unknown ARCHIVE_PATH variable.")

        if name != repo:
            rename_collection(repo, name)

        collection_to_file(name, path)

        if name != repo:
            rename_collection(name, repo)
    except Exception as e:
        return redirect("/schema/manage?error=" + e.message)

    message = "Archived " + repo + " to " + filename + "."
    return redirect("/schema/manage?message=" + message)

@app.route("/schema/manage/delete", methods=["POST"])
def manage_delete():

    repo = request.form["repository"]

    try:
        from schema.management import delete_collection
        delete_collection(repo)
    except Exception as e:
        return redirect("/schema/manage?error=" + e.message)

    message = "Deleted " + repo + " from the database."
    return redirect("/schema/manage?message=" + message)

@app.route("/schema/manage/local/install", methods=["POST"])
def manage_local_install():

    repo = request.form["repository"]

    try:
        from schema.management import file_to_collection, ARCHIVE_PATH
        path = os.environ[ARCHIVE_PATH] if ARCHIVE_PATH in os.environ else None

        if path is None:
            raise Exception("Unknown ARCHIVE_PATH variable.")

        path = path + "/" + repo + ".gz"

        file_to_collection(path)
    except Exception as e:
        return redirect("/schema/manage?error=" + e.message)

    message = "Installed " + repo + "."
    return redirect("/schema/manage?message=" + message)

@app.route("/schema/manage/local/publish", methods=["POST"])
def manage_local_publish():

    repo = request.form["repository"]

    try:
        from schema.management import publish_archive
        publish_archive(repo)
    except Exception as e:
        return redirect("/schema/manage?error=" + e.message)

    message = "Published " + repo + "."
    return redirect("/schema/manage?message=" + message)

@app.route("/schema/manage/local/delete", methods=["POST"])
def manage_local_delete():

    repo = request.form["repository"]

    try:
        from schema.management import delete_local_archive
        delete_local_archive(repo)
    except Exception as e:
        return redirect("/schema/manage?error=" + e.message)

    message = "Deleted archive " + repo + "."
    return redirect("/schema/manage?message=" + message)

@app.route("/schema/manage/remote/download", methods=["POST"])
def manage_remote_download():

    repo = request.form["repository"]

    try:
        from schema.management import download_archive
        download_archive(repo)
    except Exception as e:
        return redirect("/schema/manage?error=" + e.message)

    message = "Downloaded " + repo + "."
    return redirect("/schema/manage?message=" + message)


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 5005

    import sys

    for arg in sys.argv:
        if '=' in arg:
            k = arg.split("=")[0]
            v = arg.split("=")[1]

            if k == "host":
                host = v
            if k == "port":
                port = int(v)

    app.run(host=host, port=port, debug=True)
