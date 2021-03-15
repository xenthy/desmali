#!/usr/bin/env python3

import os
import json


from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


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


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/result', methods=['GET','POST'])
def result():
    #save apk to .tmp folder
    upload_file = request.files['file']
    upload_file.save("../.tmp/"+upload_file.filename)

    # get obfuscation options 
    options = request.form.getlist('options')
    string_obf = True if '1' in options else False
    cfg_obf = True if '2' in options else False
    remove_log = True if '3' in options else False
    
    #do all the stuff
    print(string_obf,cfg_obf,remove_log)
    size_overhead = "10mb"
    time_overhead = "10sec"
    instructions = "20"


    # Find and display all file and folder for jstree
    path = ""
    unique_nodes = []
    for root, dirs, files in os.walk("../.tmp"):
        for name in files:
            path = os.path.join(root,name)
            nodes = get_nodes_from_path(path)
            for node in nodes:
                if not any(node.is_equal(unode) for unode in unique_nodes):
                    unique_nodes.append(node)
    
    data = [node.as_json() for node in unique_nodes]
    return render_template("result.html", \
        apk_name = upload_file.filename, \
        size_overhead = size_overhead, \
        time_overhead = time_overhead, \
        instructions = instructions, \
        data = data)

@app.route('/viewlines', methods=['POST'])
def viewlines():
    try:
        file_name = request.json["data"].strip()
        with open (file_name, "r") as f:
            content = f.read()
        return jsonify(content)
    except:
        return "Non readable ascii"




if __name__ == "__main__":
    app.run(port=6969)
