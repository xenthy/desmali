#!/usr/bin/env python3

import os
import math

from flask import Flask, request, render_template, jsonify, send_from_directory
from waitress import serve

from desmali.all import *
from desmali.extras import logger
from main import pre_obfuscate, post_obfuscate

app = Flask(__name__)

OBFUSCATION_METHODS = [PurgeLogs,
                       GotoInjector,
                       RandomiseLabels,
                       StringEncryption,
                       RenameMethod,
                       RenameClass,
                       BooleanArithmetic
                       ]

DIR_MAPPING = {}

PROGRESS = {"completion": 0, "status": ""}


class Node:
    """
    Node object for each item in a directory path
    """

    def __init__(self, nid, text, parent, icon):
        self.id = nid
        self.text = text
        self.parent = parent
        self.icon = icon

    def is_equal(self, node):
        return self.id == node.id

    def as_json(self):
        return dict(
            id=self.id,
            parent=self.parent,
            text=self.text,
            icon=self.icon
        )


def get_nodes_from_path(path):
    # perform mapping of parent node and child nodes in the path
    nodes = []
    path_nodes = path.split("/")
    for idx, node_name in enumerate(path_nodes):
        parent = None
        node_id = "/".join(path_nodes[0:idx+1])
        if idx != 0:
            parent = "/".join(path_nodes[0:idx])
        else:
            parent = "#"

        if os.path.isfile(node_id):
            icon = "/static/jsTree/themes/default/file.png"
        else:
            icon = "/static/jsTree/themes/default/dir.gif"
        nodes.append(Node(node_id, node_name, parent, icon))
    return nodes


def get_filetree():
    # Find and display all file and folder in obfuscated folder for jstree
    path = ""
    unique_nodes = []
    for root, _, files in os.walk("./.tmp/obfuscated"):
        for name in files:
            path = os.path.join(root, name)
            nodes = get_nodes_from_path(path)
            for node in nodes:
                if not any(node.is_equal(unode) for unode in unique_nodes):
                    unique_nodes.append(node)

    data = [node.as_json() for node in unique_nodes]
    return data


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/config', methods=['POST'])
def config():
    # save apk to folder
    upload_file = request.files['file']
    upload_file.save("./.tmp/" + upload_file.filename)

    return render_template("config.html", apk_name=upload_file.filename)


@app.route('/download', methods=['GET'])
def download():
    # Download obfuscated file
    download_dir = os.path.join(os.getcwd(), ".tmp")
    return send_from_directory(directory=download_dir,
                               filename="signed.apk",
                               as_attachment=True,
                               attachment_filename=request.args['q'])


@app.route('/result', methods=['GET', 'POST'])
def result():
    # PROGRESS BAR
    global PROGRESS
    if request.method == "GET":
        return PROGRESS

    # get file name , keypass, kspass, jks_key_file
    apk_name = request.form.get("apk_name")
    ks_pass = request.form.get("ks-pass")
    key_pass = request.form.get("key-pass")
    key_file = request.files["file"]
    key_path = "./.tmp/" + key_file.filename
    key_file.save(key_path)

    # get obfuscation options, purge_logs options
    options = request.form.getlist('options')
    purge_options = request.form.getlist('purge_options')
    increment = 100.0 / (3 + len(options))

    # decompiling apk file
    PROGRESS["status"] = "Decoding & Analysing APK"
    dissect, apktool = pre_obfuscate("./.tmp/" + apk_name)
    PROGRESS["completion"] = PROGRESS["completion"] + increment

    # set purge_logs options
    purge_options_dict = dict()
    for option in purge_options:
        purge_options_dict[option] = True

    # Run obfuscation methods
    for method in OBFUSCATION_METHODS:
        if method_name := method.__name__ in options:
            PROGRESS["status"] = f"Performing {method.__name__}"
            if method_name == "PurgeLogs":
                method(dissect).run(**purge_options_dict)
            else:
                method(dissect).run()
            PROGRESS["completion"] = PROGRESS["completion"] + increment

    # Rebuilding, Zipaligning and Signing APK
    PROGRESS["status"] = "Rebuilding, Zipaligning & Signing APK"
    post_obfuscate(apktool, key_path,
                   ks_pass, key_pass)
    PROGRESS["completion"] = PROGRESS["completion"] + increment

    # update smali file after decompiling new apk
    dissect.smali_files(force=True)

    # get number of smali lines before and after obfuscation
    initial_num, current_num = dissect.line_count_info()
    logger.info(f"Line count: Initial: {initial_num} - " +
                f"Current: {current_num} - " +
                "Added: {:.2f}".format(current_num / initial_num))

    # get line count and size statistics
    stats: Dict[str] = dict()
    stats["name"] = apk_name

    # get size difference
    original_size, current_size = dissect.file_size_difference("./.tmp/signed.apk")
    stats["original_size"] = f"{original_size:,}"
    stats["current_size"] = f"{current_size:,}"
    stats["factor_size"] = "{:.2f}x".format(current_size / original_size)
    if (current_size / original_size) < 1:
        stats["increase_size"] = 0
    else:
        stats["increase_size"] = int(math.ceil(((current_size / original_size) - 1) * 100))

    # get line count difference
    original_lines, current_lines = dissect.line_count_info()
    stats["original_lines"] = f"{original_lines:,}"
    stats["current_lines"] = f"{current_lines:,}"
    stats["factor_lines"] = "{:.2f}x".format(current_lines / original_lines)
    if (current_lines / original_lines) < 1:
        stats["increase_lines"] = 0
    else:
        stats["increase_lines"] = int(math.ceil(((current_lines / original_lines - 1)) * 100))

    # get files in obfuscated directory for display in jstree
    global DIR_MAPPING
    DIR_MAPPING = dissect.dir_mapping
    PROGRESS["status"] = "Getting Filetree data"
    data = get_filetree()
    PROGRESS["completion"] = 100

    return render_template("result.html", stats=stats, data=data)


@ app.route('/viewlines', methods=['POST'])
def viewlines():
    # return content of file in json format
    try:
        file_path = request.json["data"].strip()
        with open(file_path, "r") as file:
            content = file.read()
        return jsonify(content)
    except:
        return "Non readable ascii"


@ app.route('/comparelines', methods=['POST'])
def comaprelines():
    # return file difference of files in json format
    try:
        global DIR_MAPPING
        file_path = request.json["data"].strip()
        diff: Diff = Diff()
        if DIR_MAPPING[file_path] is not None:
            html = diff.generate_diff(DIR_MAPPING[file_path], file_path)
            return jsonify(html)
        return "No changes or not available"
    except:
        return "No changes or not available"


if __name__ == "__main__":
    # logger.info("server running at http://localhost:6969")
    # app.run(host="0.0.0.0", port=6969)
    serve(app, host="0.0.0.0", port=6969)
