"""Visualizes a scene graph stored in a json in a webpage.
"""

import argparse
import json
import os
import webbrowser


def generate_graph_js(graph, js_file):
    """Converts a json into a readable js object.

    Args:
        graph: A scene graph object.
        js_file: The javascript file to write to.
    """
    f = open(js_file, 'w')
    f.write('var graph = ' + json.dumps(graph))
    f.close()

def generate_graph_js_3DSSG(graph_obj, graph_rel, js_file1, js_file2):
    """Converts a json into a readable js object.

    Args:
        graph: A scene graph object.
        js_file: The javascript files to write to.
    """
    f = open(js_file1, 'w')
    f.write('var graph obj = ' + json.dumps(graph_obj))
    f.close()
    
    f = open(js_file2, 'w')
    f.write('var graph obj = ' + json.dumps(graph_rel))
    f.close()


def visualize_scene_graph(graph, js_file):
    """Creates an html visualization of the scene graph.

    Args:
        graph: A scene graph object.
        js_file: The javascript file to write to.
    """
    scene_graph = {'objects': [], 'attributes': [], 'relationships': [], 'url': graph['url']}
    for obj in graph['objects']:
        name = ''
        if 'name' in obj:
            name = obj['name']
        elif 'names' in obj and len(obj['names']) > 0:
            name = obj['names'][0]
        scene_graph['objects'].append({'name': name})
    scene_graph['attributes'] = graph['attributes']
    scene_graph['relationships'] = graph['relationships']
    generate_graph_js(scene_graph, js_file)
    print(scene_graph)
    webbrowser.open('file://' + os.path.realpath('graphviz.html'))

def visualize_scene_graph_3DSSG(graph_obj, graph_rel, js_file1, js_file2):
    """Creates an html visualization of the scene graph with 3DSSG data.
    
    Args:
        graph_obj: Scene graph objects
        graph_rel: Relationships between the objects
        js_file: The javascript file to write to.
    """
    scene_graph = {'objects': [], 'attributes': [], 'relationships': [], 'url': 'https://graphviz.jpg'}
    
    # objects.json
    for scan in graph_obj['scans']:
        for obj in scan['objects']:
            label = ''
            if 'label' in obj:
                label = obj['label']
            scene_graph['objects'].append({'name': label})
        scene_graph['attributes'] = scan['attributes']
    
    # relationships.json
    for scan in graph_rel['scans']:
        scene_graph['relationships'] = scan['relationships']
        generate_graph_js_3DSSG(scene_graph, js_file)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--graph', type=str,
                        default='example_graph.json',
                        help='Location of scene graph file to visualize.')
    parser.add_argument('--js-file', type=str,
                        default='scene_graph.js',
                        help='Temporary file generated to enable visualization.')
    args = parser.parse_args()
    graph = json.load(open(args.graph))
    visualize_scene_graph(graph, args.js_file)
