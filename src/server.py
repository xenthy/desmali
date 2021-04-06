#!/usr/bin/env python3

import os
import json
import math
import time

from flask import Flask, request, render_template, jsonify, send_from_directory, Response
from waitress import serve

from desmali.extras import logger
from desmali.all import *
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
    def __init__(self, id, text, parent, icon):
        self.id = id
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
    # Find and display all file and folder for jstree
    path = ""
    unique_nodes = []
    for root, dirs, files in os.walk("./.tmp/obfuscated"):
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
    d = os.path.join(os.getcwd(), ".tmp")
    return send_from_directory(directory=d, filename="signed.apk", as_attachment=True, attachment_filename=request.args['q'])


@app.route('/result', methods=['GET', 'POST'])
def result():
    # PROGRESS BAR
    global PROGRESS
    if request.method == "GET":
        return PROGRESS

    # get file name , keypass
    apk_name = request.form.get("apk_name")
    ks_pass = request.form.get("ks-pass")
    key_pass = request.form.get("key-pass")

    # get options
    options = request.form.getlist('options')
    purge_options = request.form.getlist('purge_options')
    increment = 100.0 / (3 + len(options))

    PROGRESS["status"] = "Decoding & Analysing APK"
    dissect, apktool = pre_obfuscate("./.tmp/" + apk_name)
    PROGRESS["completion"] = PROGRESS["completion"] + increment

    purge_options_dict = dict()
    for option in purge_options:
        purge_options_dict[option] = True

    for method in OBFUSCATION_METHODS:
        if method.__name__ in options:
            PROGRESS["status"] = "Performing " + method.__name__
            obf_method = method(dissect)
            if method.__name__ == "PurgeLogs":
                obf_method.run(**purge_options_dict)
            else:
                obf_method.run()
            PROGRESS["completion"] = PROGRESS["completion"] + increment

    PROGRESS["status"] = "Rebuilding, Zipaligning & Signing APK"
    post_obfuscate(apktool, "./ict2207-test-key.jks",
                   "nim4m4h4om4?", "nim4m4h4om4?")
    PROGRESS["completion"] = PROGRESS["completion"] + increment

    # update smali file after decompiling new apk
    dissect.smali_files(force=True)

    # get number of smali lines before and after obfuscation
    initial_num, current_num = dissect.line_count_info()
    logger.info(f"Line count: Initial: {initial_num} - " +
                f"Current: {current_num} - " +
                "Added: {:.2f}".format(current_num / initial_num))

    # do all the stuff
    stats = {}
    stats["name"] = apk_name

    original_size, current_size = dissect.file_size_difference("./.tmp/signed.apk")
    stats["original_size"] = f"{original_size:,}"
    stats["current_size"] = f"{current_size:,}"
    stats["increase_size"] = original_size - current_size
    stats["factor_size"] = "{:.2f}x".format(current_size / original_size)
    if (current_size / original_size) < 1:
        stats["increase_size"] = 0
    else:
        stats["increase_size"] = int(math.ceil(((current_size / original_size) - 1) * 100))
    print(stats["increase_size"])

    original_lines, current_lines = dissect.line_count_info()
    stats["original_lines"] = f"{original_lines:,}"
    stats["current_lines"] = f"{current_lines:,}"
    if (current_lines / original_lines) < 1:
        stats["increase_lines"] = 0
    else:
        stats["increase_lines"] = int(math.ceil(((current_lines / original_lines - 1 )) * 100))
    print(stats["increase_lines"])

    stats["factor_lines"] = "{:.2f}x".format(current_lines / original_lines)

    global DIR_MAPPING
    DIR_MAPPING = dissect.dir_mapping

    # get files
    PROGRESS["status"] = "Getting Filetree data"
    data = get_filetree()
    PROGRESS["completion"] = 100
    return render_template("result.html",
                           stats=stats,
                           data=data)


@ app.route('/viewlines', methods=['POST'])
def viewlines():
    try:
        file_path = request.json["data"].strip()
        with open(file_path, "r") as f:
            content = f.read()
        return jsonify(content)
    except:
        return "Non readable ascii"


@ app.route('/comparelines', methods=['POST'])
def comaprelines():
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
    logger.info("server running at http://localhost:6969")
    # app.run(host="0.0.0.0", port=6969)
    serve(app, host="0.0.0.0", port=6969)
