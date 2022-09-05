import json

with open('relationships.json') as f:
    relationships = json.load(f)['scans']

new_relationships = {}

for scene in relationships:
    new_relationships[scene['scan']] = scene['relationships']

with open('new_relationships.json', 'w') as new:
    json.dump(new_relationships, new)


