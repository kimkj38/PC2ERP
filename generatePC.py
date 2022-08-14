import json
import numpy as np
from plyfile import PlyData, PlyElement
import os

# scan id
scan_id = "4acaebc8-6c10-2a2a-8525-fe9c4b7f4b25"

# get rgb from hex code
def hex2rgb(hex):
    hex = hex.lstrip('#')
    r,g,b = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    return r,g,b

# class dictionary
word2idx = {} # key: object name, value: object id
index = 0
file = open("classes.txt", 'r')
category = file.readline()[:-1]
while category:
    word2idx[category] = index
    category = file.readline()[:-1]
    index += 1

# subset json
with open('subset.json') as f:
    subset_file = json.load(f)["scans"]

# original json
with open('original.json') as f:
    original_file = json.load(f)["scans"]

# point cloud
with open('{}/mesh.refined.v2.obj'.format(scan_id)) as f:
    point_cloud = []
    while 1:
        line = f.readline()
        if not line:
            break
        strs = line.split(" ")
        if strs[0] == "v":
            point_cloud.append((float(strs[1]), float(strs[2]), float(strs[3])))
    point_cloud = np.array(point_cloud)


# segment & point cloud correspondence
segments = {}  # key:segment id, value: points belong to this segment
with open("{}/mesh.refined.0.010000.segs.v2.json".format(scan_id), 'r') as f:
    seg_indices = json.load(f)["segIndices"]
    for index, i in enumerate(seg_indices):
        if i not in segments:
            segments[i] = []
        segments[i].append(point_cloud[index])

# filter the object which does not belong to this split
# obj_id_list = []
# for obj_id, _ in subset_file["objects"].items():
#     obj_id_list.append(int(obj_id))

# seg groups
with open("{}/semseg.v2.json".format(scan_id), 'r') as f:
    obj2pc = {} # key: object id, value: point cloud
    seg2obj = {} # key: segment id, value: object id
    seg_groups = json.load(f)["segGroups"]
    for object in seg_groups:
        object_id = object["id"]
        # if object_id not in obj_id_list:
        #     continue
        # if object["label"] not in  word2idx:
        #     continue

        seg_ids = object["segments"]
        obj2pc[object_id] = []
        for seg_id in seg_ids:
            seg2obj[seg_id] = object_id
            for pc in segments[seg_id]:
                #print(np.concatenate((obj2pc[object_id], pc.reshape(1,-1)), axis=0))
                obj2pc[object_id] = pc.reshape(1, -1) if len(obj2pc[object_id]) == 0 else np.concatenate((obj2pc[object_id], pc.reshape(1, -1)), axis=0)


# hex code dictionary
for i, scan in enumerate(original_file):
    if scan["scan"] == scan_id:
        hex_dict = {} # key: object id, value: hex code
        global_dict = {} # key: object id, value: global id
        objects = original_file[i]["objects"]
        for object in objects:
            hex_dict[object["id"]] = object["ply_color"]
            global_dict[object["id"]] = object["global_id"]



for i, scan in enumerate(subset_file):
    if scan["scan"] == scan_id:
        
        # split name
        split = subset_file[i]["split"] 
        ply_name = scan_id + "_{}.ply".format(split) 
        # object ids
        object_ids = list(subset_file[i]["objects"].keys())
        vertex = []
        for obj_id in object_ids:
            pc = obj2pc[int(obj_id)]
            global_id = int(global_dict[obj_id])
            r, g, b = hex2rgb(hex_dict[obj_id])

            for x,y,z in pc:
                if len(vertex) == 0:
                    vertex = [(x, y, z, r, g, b, obj_id, global_id)]
                    
                else:
                    vertex.append((x, y, z, r, g, b, obj_id, global_id))
            
        vertex = np.array(vertex, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('r', 'u1'), ('g', 'u1'), ('b', 'u1'),
                    ('object_id', 'ushort'), ('global_id', 'ushort')])
        

            # print(type((np.concatenate((pc, np.tile([r, g, b, obj_id, global_id], (len(pc),1))), axis=1).astype('f4'))[0]))
            # break

            # if len(vertex) == 0:        
            #     vertex = np.array(np.concatenate((pc, np.tile([r, g, b, obj_id, global_id], (len(pc),1))), axis=1).astype('f4'), 
            #            dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('r', 'u1'), ('g', 'u1'), ('b', 'u1')])
            # else:
            #     obj_vertex = np.array(np.concatenate((pc, np.tile([r, g, b, obj_id, global_id], (len(pc),1))), axis=1).astype('f4'), 
            #            dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('r', 'u1'), ('g', 'u1'), ('b', 'u1')])
            #     vertex = np.concatenate((vertex, obj_vertex), axis=0)


        el = PlyElement.describe(vertex, 'vertex')
        PlyData([el], text=True).write(os.path.join(scan_id, ply_name))
    
        
        # # original json file to get information
        # original_objects = original_file[i]["objects"]




