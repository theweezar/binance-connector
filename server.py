from flask import Flask, request, jsonify, render_template_string
import os
import hashlib
import json
from html import escape
from py.quantdeepseek import Quant_DeepSeek_CLI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, "ignore")
WEB_DIR = os.path.join(BASE_DIR, "web")
DIST_DIR = os.path.join(WEB_DIR, "dist")
FILES_ROOT = os.path.join(WEB_DIR, "dist", "file")

app = Flask(__name__, static_folder=DIST_DIR)


def json_safe_load(json_str):
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


def list_files_tree(dir_path, base_path=None):
    """
    Reimplements PHP listFilesTree in Python, returns an HTML string with nested <ul>.
    """
    base_path = base_path or os.path.realpath(dir_path)
    if not os.path.isdir(dir_path):
        return '<div class="text-danger">Directory not found.</div>'

    try:
        items = sorted(os.listdir(dir_path))
    except OSError:
        return ""

    html = ['<ul class="list-group list-group-flush">']
    for item in items:
        if item in (".", ".."):
            continue
        full = os.path.join(dir_path, item)
        try:
            real_full = os.path.realpath(full)
        except Exception:
            real_full = full
        rel = real_full.replace(base_path, "").lstrip(os.sep)
        safe_item = escape(item)
        if os.path.isdir(full):
            # folder: collapsible
            id_ = "d_" + hashlib.md5(rel.encode("utf-8")).hexdigest()
            html.append('<li class="list-group-item p-0 border-0">')
            html.append('<div class="d-flex align-items-center px-2 py-1">')
            html.append(
                f'<button class="btn btn-sm btn-link text-decoration-none me-2 toggle-folder" data-target="#{id_}" aria-expanded="false">▶</button>'
            )
            html.append(f'<strong class="me-2">{safe_item}</strong>')
            html.append("</div>")
            html.append(f'<div id="{id_}" class="ps-3" style="display:none">')
            html.append(list_files_tree(full, base_path))
            html.append("</div>")
            html.append("</li>")
        else:
            # file
            rel_esc = escape(rel)
            html.append('<li class="list-group-item px-2 py-1">')
            html.append(
                f'<a href="?source={rel_esc}" class="file-item stretched-link" data-path="{rel_esc}">{safe_item}</a>'
            )
            html.append("</li>")
    html.append("</ul>")
    return "".join(html)


@app.route("/", methods=["GET"])
def index():
    # read the HTML template file and render with file_tree injected
    template_path = os.path.join(WEB_DIR, "index.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
    except Exception as e:
        return f"Template not found: {e}", 500

    file_tree_html = list_files_tree(FILES_ROOT, FILES_ROOT)
    return render_template_string(template, file_tree=file_tree_html)


@app.route("/fetch", methods=["GET"])
def fetch_handler():
    try:
        source = request.args.get("source", "")
        rules = json_safe_load(request.args.get("rules", ""))
        config = json_safe_load(request.args.get("config", ""))
        _input = os.path.join(SOURCE_DIR, source)
        _output = os.path.join(FILES_ROOT, source)
        quant = Quant_DeepSeek_CLI(
            input=_input, output=_output, config=config, allowed_rules=rules
        )
        quant.run_specific_config()
        return jsonify(success=True)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify(success=False, error=f"{e}")


if __name__ == "__main__":
    # simple dev server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
