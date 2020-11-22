import os
import sys
import flask
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / 'lib'))
import netmap
import netmap_cache

run_dir = Path("run").resolve()
run_dir.mkdir(exist_ok=True)
app = flask.Flask(__name__)

def map_merge_attributes(nodes, links, saved_attributes):
    locations = { n['key']: n['loc'] for n in saved_attributes['nodeDataArray'] if 'loc' in n }
    is_exanded = { n['key']: n['is_subgraph_expanded'] for n in saved_attributes['nodeDataArray'] if 'is_subgraph_expanded' in n }
    for node in nodes:
        if node['key'] in locations:
            node['loc'] = locations[node['key']]
            node['is_layout_positioned'] = "false"
        if node['key'] in is_exanded:
            node['is_subgraph_expanded'] = is_exanded[node['key']]
    return nodes, links

def map_copy_settings(map_dict, saved_attributes):
    if 'netmap_settings' in saved_attributes:
        map_dict['netmap_settings'] = saved_attributes['netmap_settings']

@app.route('/')
def index_view():
    if 'NETMAP_INPUT_DATA_DIRECTORY' not in os.environ:
        raise Exception("NETMAP_INPUT_DATA_DIRECTORY environment variable must be set")
    if 'NETMAP_DEBUG' not in os.environ:
        raise Exception("NETMAP_DEBUG environment variable must be set")
    input_dir = Path(os.environ['NETMAP_INPUT_DATA_DIRECTORY']).resolve()
    network_list = [str(x.name) for x in input_dir.iterdir() if x.is_dir()]
    return flask.render_template('index.html', input_data_directory=input_dir, network_list=network_list, program_header=netmap.PROGRAM_HEADER)

@app.route('/map/')
def netmap_empty_view():
    return flask.redirect(flask.url_for('index_view'))

@app.route('/map/<network_name>/')
def netmap_view(network_name):
    input_dir = Path(os.environ['NETMAP_INPUT_DATA_DIRECTORY'])
    anonymize_hex_salt = os.environ['NETMAP_ANONYMIZE_HEX_SALT']
    if len(anonymize_hex_salt) == 0:
        network_name_displayed = network_name
        anonymize_hex_salt = None
    else:
        network_name_displayed = "%s (anononymized)" % network_name
    debug = int(os.environ['NETMAP_DEBUG'])
    network_dir = input_dir / network_name

    try:
        nm = netmap_cache.Netmap_cache(network_dir, run_dir, anonymize_hex_salt=anonymize_hex_salt, debugval=debug)
    except Exception as e:
        print("Exception: %s" % e)
        print("redirecting to index")
        return flask.redirect(flask.url_for('index_view'))
    nm.process()
    nodes, links = nm.map()

    saved_attributes_file = run_dir / ("%s_saved_attributes.json" % network_name)
    if saved_attributes_file.exists():
        saved_attributes = json.loads(saved_attributes_file.read_text())
        map_merge_attributes(nodes, links, saved_attributes)

    map_dict = {
        "class": "go.GraphLinksModel",
        "nodeDataArray": nodes,
        "linkDataArray": links,
    }
    if saved_attributes_file.exists():
        map_copy_settings(map_dict, saved_attributes)

    if app.debug:
        json_debug = json.dumps(map_dict, indent=4, sort_keys=True)
        print(json_debug)
        json_debug_file = run_dir / "debug.json"
        json_debug_file.write_text(json_debug)
        print("wrote json to %s" % json_debug_file)
        gojs_version = "go-debug.js"
    else:
        gojs_version = "go.js"

    return flask.render_template('map.html', network_name=network_name_displayed, map_dict=map_dict, gojs_version=gojs_version, network_statistics=nm.stats, program_header=netmap.PROGRAM_HEADER)

@app.route('/map/<network_name>/save/', methods=["POST"])
def save(network_name):
    req = flask.request.get_json()
    savefile = run_dir / ("%s_saved_attributes.json" % network_name)
    savefile.write_text(json.dumps(req, indent=4, sort_keys=True))
    print("saved to %s" % savefile)
    return "Saved", 200

@app.route('/map/<network_name>/reset/')
def reset(network_name):
    req = flask.request.get_json()
    savefile = run_dir / ("%s_saved_attributes.json" % network_name)
    if savefile.exists():
        savefile.unlink()
        print("deleted %s" % savefile)
    return "Deleted", 200
