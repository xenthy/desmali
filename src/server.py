#!/usr/bin/env python3

import os
import json
from flask import Flask, request, render_template, jsonify, send_from_directory
from waitress import serve

from desmali.extras import logger
from desmali.all import *
from main import pre_obfuscate, post_obfuscate


app = Flask(__name__)
OBFUSCATION_METHODS = [PurgeLogs,
                       RenameMethod,
                       RenameClass,
                       StringEncryption,
                       GotoInjector,
                       ReorderLabels,
                       FakeBranch
                       ]


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
    for root, dirs, files in os.walk("./.tmp"):
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
    return send_from_directory(directory=d, filename="signed.apk", as_attachment=True)


@app.route('/result', methods=['POST'])
def result():

    # get file name , keypass
    apk_name = request.form.get("apk_name")
    ks_pass = request.form.get("ks-pass")
    key_pass = request.form.get("key-pass")

    dissect, apktool = pre_obfuscate("./.tmp/" + apk_name)

    # get options
    options = request.form.getlist('options')
    purge_options = request.form.getlist('purge_options')

    purge_options_dict = dict()
    for option in purge_options:
        purge_options_dict[option] = True

    for method in OBFUSCATION_METHODS:
        if method.__name__ in options:
            obf_method = method(dissect)
            if method.__name__ == "PurgeLogs":
                obf_method.run(**purge_options_dict)
            else:
                obf_method.run()

    post_obfuscate(apktool, "./ict2207-test-key.jks", "nim4m4h4om4?", "nim4m4h4om4?")

    # get number of smali lines before and after obfuscation
    initial_num, current_num = dissect.line_count_info()
    logger.info(f"Line count: Initial: {initial_num} - " +
                f"Current: {current_num} - " +
                "Added: {:.2f}".format(current_num / initial_num))

    # do all the stuff
    stats = {}
    stats["name"] = apk_name
    stats["size_overhead"] = "10mb"
    stats["time_overhead"] = "10sec"
    stats["instructions"] = "20"

    # get files
    data = get_filetree()
    return render_template("result.html",
                           stats=stats,
                           data=data)


@app.route('/viewlines', methods=['POST'])
def viewlines():
    try:
        file_name = request.json["data"].strip()
        with open(file_name, "r") as f:
            content = f.read()
        return jsonify(content)
    except:
        return "Non readable ascii"


if __name__ == "__main__":
    logger.info("server running at http://localhost:6969")
    app.run(host="0.0.0.0", port=6969)
    # serve(app, host="0.0.0.0", port=6969)
